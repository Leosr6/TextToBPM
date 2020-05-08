from copy import copy
from core.Base import Base
from utils import Processing
from utils.Constants import *
from data.BPMNElements import *
from data.SentenceElements import *
from data.TextElements import DummyAction


class ProcessElementsBuilder(Base):

    def __init__(self, world_model):
        self.f_world = world_model
        self.f_model = ProcessModel()
        self.f_action_flow_map = {}
        self.f_actor_name_map = {}
        self.f_name_pool_map = {}
        self.f_main_pool = None
        self.f_not_assigned = []
        self.f_last_pool = None

    def create_process_model(self):
        self.f_main_pool = Pool("Pool")
        self.f_model.nodes.append(self.f_main_pool)

        self.create_actions()
        self.build_sequence_flows()
        self.remove_dummies()
        self.finish_dangling_ends()
        # self.process_meta_activities()

        if len(self.f_main_pool.process_nodes) == 0:
            self.f_model.remove_node(self.f_main_pool)

        return self.f_model

    def create_actions(self):
        for action in self.f_world.f_actions:
            if self.is_event_action(action) or action.f_marker == IF or action.f_markerFromPP:
                flow_object = self.create_event_node(action)
            else:
                flow_object = Task(action)

            self.f_model.nodes.append(flow_object)
            self.f_action_flow_map[action] = flow_object

            if action.f_xcomp:
                self.f_action_flow_map[action.f_xcomp] = flow_object

            lane = None
            if not WordNetWrapper.is_weak_action(action) and action.f_actorFrom:
                lane = self.get_lane(action.f_actorFrom)

            if not lane:
                if not self.f_last_pool:
                    self.f_not_assigned.append(flow_object)
                else:
                    self.f_last_pool.process_nodes.append(flow_object)
            else:
                lane.process_nodes.append(flow_object)
                for unass_object in self.f_not_assigned:
                    lane.process_nodes.append(unass_object)
                self.f_not_assigned.clear()
                self.f_last_pool = lane

    def build_sequence_flows(self):
        for flow in self.f_world.f_flows:
            if flow.f_type == SEQUENCE and len(flow.f_multiples) == 1:
                sequence_flow = SequenceFlow(self.to_process_node(flow.f_single),
                                             self.to_process_node(flow.f_multiples[0]))
                self.f_model.edges.append(sequence_flow)
            elif flow.f_type == EXCEPTION:
                exception_event = Event(flow.f_single, INTERMEDIATE_EVENT, ERROR_EVENT)
                self.f_model.nodes.append(exception_event)
                task = self.to_process_node(flow.f_single)
                exception_event.parent_node = task
                self.add_to_same_lane(task, exception_event)

                sequence_flow = SequenceFlow(exception_event,
                                             self.to_process_node(flow.f_multiples[0]))
                self.f_model.edges.append(sequence_flow)
            elif flow.f_direction == SPLIT:
                if len(flow.f_multiples) == 1:
                    event = self.to_process_node(flow.f_multiples[0])
                    event.class_sub_type = CONDITIONAL_EVENT
                    self.add_to_prevalent_lane(flow, event)
                    sequence_flow = SequenceFlow(self.to_process_node(flow.f_single), event)
                else:
                    gateway = self.create_gateway(flow)
                    self.add_to_prevalent_lane(flow, gateway)
                    sequence_flow = SequenceFlow(self.to_process_node(flow.f_single), gateway)
                    for action in flow.f_multiples:
                        internal_flow = SequenceFlow(gateway, self.to_process_node(action))
                        self.f_model.edges.append(internal_flow)
                self.f_model.edges.append(sequence_flow)
            elif flow.f_direction == JOIN:
                if len(flow.f_multiples) > 1:
                    gateway = self.create_gateway(flow)
                    sequence_flow = SequenceFlow(gateway, self.to_process_node(flow.f_single))
                    self.f_model.edges.append(sequence_flow)
                    self.add_to_prevalent_lane(flow, gateway)
                    for action in flow.f_multiples:
                        internal_flow = SequenceFlow(self.to_process_node(action), gateway)
                        self.f_model.edges.append(internal_flow)

    def remove_dummies(self):
        for action in self.f_world.f_actions:
            if isinstance(action, DummyAction) or action.f_transient:
                self.remove_node(self.to_process_node(action))

    def finish_dangling_ends(self):
        source_map = {}
        target_map = {}

        # Calculating the occurrences of each node as a source and as a target
        for edge in self.f_model.edges:
            source_map[edge.source] = source_map.get(edge.source, 0) + 1
            target_map[edge.target] = target_map.get(edge.target, 0) + 1

        current_nodes = copy(self.f_model.nodes)

        for node in current_nodes:
            if isinstance(node, Task) or isinstance(node, Gateway) or (isinstance(node, Event) and node.class_type == INTERMEDIATE_EVENT):
                # If the node is not present, add it with 0 occurrences
                source_map.setdefault(node, 0)
                target_map.setdefault(node, 0)

                if source_map[node] == 0:
                    if isinstance(node, Gateway) and node.element.f_direction == JOIN:
                        for element in node.element.f_multiples:
                            node = self.to_process_node(element)
                            if node:
                                self.create_end_event(node)
                    else:
                        self.create_end_event(node)
                if target_map[node] == 0:
                    if isinstance(node, Event) and node.class_type == INTERMEDIATE_EVENT and node.parent_node:
                        continue
                    else:
                        self.create_start_event(node)

    def process_meta_activities(self):
        for action in self.f_world.f_actions:
            if action.f_actorFrom and action.f_actorFrom.f_metaActor:
                if WordNetWrapper.is_verb_of_type(action.f_name, END_VERB):
                    node = self.f_action_flow_map[action]
                    successors = self.f_model.get_successors(node)
                    self.remove_node(node)
                    if len(successors) == 1 and isinstance(successors[0], Event) and successors[0].class_type == END_EVENT:
                        if action.f_name == TERMINATE:
                            successors[0].class_sub_type = TERMINATE_EVENT
                elif WordNetWrapper.is_verb_of_type(action.f_name, START_VERB):
                    node = self.f_action_flow_map[action]
                    predecessors = self.f_model.get_predecessors(node)
                    if len(predecessors) == 1 and isinstance(predecessors[0], Event) and predecessors[0].class_type == START_EVENT:
                        self.remove_node(node)

    def create_start_event(self, flow_object):
        # A process model can start with a Message event
        if isinstance(flow_object, Event) and flow_object.class_sub_type != MESSAGE_EVENT:
            flow_object.class_type = START_EVENT
            flow_object.class_sub_type = None
            flow_object.sub_type = None

    def create_end_event(self, flow_object):
        element = flow_object.element

        if WordNetWrapper.is_verb_of_type(element.f_name, END_VERB):
            # A process model can end with a Message event
            if not isinstance(flow_object, Event) or flow_object.class_sub_type != MESSAGE_EVENT:
                sequence_flows = [edge for edge in self.f_model.edges if edge.target == flow_object]
                end_event = Event(element, END_EVENT)
                self.f_model.nodes.append(end_event)
                self.add_to_same_lane(flow_object, end_event)
                for sf in sequence_flows:
                    sf.target = end_event
                self.f_model.remove_node(flow_object)

    def create_event_node(self, action):
        for spec in action.f_specifiers:
            for word in spec.f_name.split(" "):
                if WordNetWrapper.is_time_period(word):
                    timer_event = Event(action, INTERMEDIATE_EVENT, TIMER_EVENT)
                    timer_event.text = spec.f_name
                    return timer_event

        if WordNetWrapper.is_verb_of_type(action.f_name, SEND_VERB) or WordNetWrapper.is_verb_of_type(action.f_name, RECEIVE_VERB):
            if not action.f_actorFrom:
                message_event = Event(action, INTERMEDIATE_EVENT, MESSAGE_EVENT)
                if WordNetWrapper.is_verb_of_type(action.f_name, SEND_VERB):
                    message_event.sub_type = THROWING_EVENT
                return message_event

        if action.f_marker in f_conditionIndicators:
            return Event(action, INTERMEDIATE_EVENT, CONDITIONAL_EVENT)

        return Event(action, INTERMEDIATE_EVENT)

    def get_lane(self, actor):
        subject = actor.f_subjectRole

        if actor.f_needsResolve:
            if isinstance(actor.f_reference, Actor):
                actor = actor.f_reference
            else:
                return None

        if not actor.f_unreal and not actor.f_metaActor and subject:
            name = self.get_name(actor, False, 1, False)
            self.f_actor_name_map[actor] = name

            if name not in self.f_name_pool_map:
                lane = Lane(actor, name, self.f_main_pool)
                self.f_main_pool.process_nodes.append(lane)
                self.f_model.nodes.append(lane)
                self.f_name_pool_map[name] = lane
                return lane
            else:
                return self.f_name_pool_map[name]

        return None

    def to_process_node(self, action):
        if action in self.f_action_flow_map:
            return self.f_action_flow_map[action]
        else:
            if isinstance(action, DummyAction):
                task = Task(action)
                self.f_action_flow_map[action] = task
                return task
            else:
                self.logger.error("FlowObject not found!")
                return None

    def create_gateway(self, flow):
        gateway = Gateway(flow)

        if flow.f_type == CONCURRENCY:
            gateway.type = PARALLEL_GATEWAY
        elif flow.f_type == MULTIPLE_CHOICE:
            gateway.type = INCLUSIVE_GATEWAY
        else:
            gateway.type = EXCLUSIVE_GATEWAY
            # Default type
            # gateway.type = EVENT_BASED_GATEWAY
            # for action in flow.f_multiples:
            #     node = self.f_action_flow_map.get(action)
            #     if isinstance(node, Event) and node.class_type == INTERMEDIATE_EVENT and not node.class_sub_type:
            #         continue
            #     else:
            #         gateway.type = EXCLUSIVE_GATEWAY
            #         break

        self.f_model.nodes.append(gateway)
        return gateway

    def add_to_prevalent_lane(self, flow, gateway):
        lane_count = {}
        actions = [flow.f_single]

        actions.extend(flow.f_multiples)

        for action in actions:
            if not isinstance(action, DummyAction):
                lane = self.get_lane_for_node(self.to_process_node(action))
                if lane:
                    lane_count[lane] = lane_count.get(lane, 0) + 1

        if len(lane_count) > 0:
            lane = max(lane_count, key=lane_count.get)
            lane.process_nodes.append(gateway)

    def add_to_same_lane(self, source, node):
        lane = self.get_lane_for_node(source)
        if lane:
            lane.process_nodes.append(node)

    def get_lane_for_node(self, source):
        for node in self.f_model.nodes:
            if isinstance(node, Lane):
                if source in node.process_nodes:
                    return node

        return None

    def remove_node(self, node):
        pred_edge = None
        succ_edge = None

        for edge in self.f_model.edges:
            if edge.target == node:
                pred_edge = edge
            if edge.source == node:
                succ_edge = edge

        self.f_model.remove_node(node)

        if pred_edge and succ_edge:
            sequence_flow = SequenceFlow(pred_edge.source, succ_edge.target)
            self.f_model.edges.append(sequence_flow)
            return sequence_flow
        else:
            return None

    def get_name(self, obj, add_det, level, compact):
        if not obj:
            return None
        if obj.f_needsResolve and isinstance(obj.f_reference, ExtractedObject):
            return self.get_name(obj.f_reference, add_det, 1, False)

        text = ""

        if add_det and obj.f_determiner in f_wantedDeterminers:
            text += obj.f_determiner + " "

        for spec in obj.get_specifiers(AMOD):
            text += spec.f_name + " "
        for spec in obj.get_specifiers(NUM):
            text += spec.f_name + " "
        for spec in obj.get_specifiers(NN):
            text += spec.f_name + " "

        text += obj.f_name

        for spec in obj.get_specifiers(NNAFTER):
            text += " " + spec.f_name

        if level <= MAX_NAME_DEPTH:
            for spec in obj.get_specifiers(PP):
                if spec.f_type == UNKNOWN and ADD_UNKNOWN_PHRASETYPES:
                    if spec.f_name.startswith(OF) or \
                            (not compact and spec.f_name.startswith((INTO, UNDER, ABOUT))):
                        text += " " + self.add_specifier(spec, level, compact)
                    elif self.consider_phrase(spec):
                        text += " " + self.add_specifier(spec, level, compact)

        if not compact:
            for spec in obj.get_specifiers(INFMOD):
                text += " " + spec.f_name
            for spec in obj.get_specifiers(PARTMOD):
                text += " " + spec.f_name

        return text

    def add_specifier(self, spec, level, compact):
        text = ""
        if spec.f_object:
            text += spec.f_headWord + " " + self.get_name(spec.f_object, True, level + 1, compact)
        else:
            text += spec.f_name
        return text

    def can_be_transformed(self, action):
        if action.f_object and not Processing.is_unreal_actor(action.f_object) \
                and not action.f_object.f_needsResolve and self.has_hidden_action(action.f_object):
            return True

        return action.f_actorFrom and Processing.is_unreal_actor(action.f_actorFrom) and self.has_hidden_action(action.f_actorFrom)

    @staticmethod
    def has_hidden_action(obj):
        can_be_gerund = False
        for spec in obj.get_specifiers(PP):
            if spec.f_name.startswith(OF):
                can_be_gerund = True
                break

        if not can_be_gerund:
            return False

        for word in obj.f_name.split():
            if WordNetWrapper.derive_verb(word):
                return True

        return False

    @staticmethod
    def is_event_action(action):
        # Checking if the verb is in the past participle
        if action.label == VBN:
            if (action.f_preAdvMod and not action.preAdvModFromSpec) or action.f_marker:
                sentence = str(action.f_sentence).lower()
                min_index = action.f_preAdvModPos if action.f_preAdvMod else action.f_markerPos
                # Checking if the sentence contains any indicators that the activity has finished
                for indicator in finishedIndicators:
                    indicator_index = sentence.find(indicator)
                    if indicator_index != -1:
                        indicator_index += len(indicator.split())
                        if min_index <= indicator_index <= action.f_word_index:
                            return True

        return False

    def transform_to_action(self, obj):
        text = ""
        for word in obj.f_name.split():
            verb = WordNetWrapper.derive_verb(word)
            if verb:
                text += verb
                break
        for spec in obj.get_specifiers(PP):
            if spec.startswith(OF) and spec.f_object:
                text += " " + self.get_name(spec.f_object, True, 1, False)

        return text

    @staticmethod
    def consider_phrase(spec):
        return spec.f_type not in (PERIPHERAL, EXTRA_THEMATIC)
