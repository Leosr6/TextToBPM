from collections import Counter
from functools import reduce
from data.SentenceElements import Action


def count_children(sentence, types):
    counter = Counter([child.label() for child in list(sentence)])
    return reduce(lambda a, b: a + counter[b], types, 0)


def find_children(sentence, types):
    types = (types,) if isinstance(types, str) else types
    children = [child for child in list(sentence) if not isinstance(child, str) and child.label() in types]
    return children


def find_dependencies(dependencies, types):
    types = (types,) if isinstance(types, str) else types
    deps = [dep for dep in dependencies if dep['dep'] in types or (dep['spec'] and dep['spec'] in types)]
    return deps


def find_sentence_index(fsentence, sentence):
    return find_array_part(fsentence.leaves(), sentence.leaves())


def find_array_part(array, part):
    indices = [i for i in range(len(array)) if array[i:i+len(part)] == part]
    if len(indices) > 0:
        return indices[0] + 1
    elif len(part) > 1:
        return find_array_part(array, part[1:])
    else:
        return -1


def find_dep_in_tree(fsentence, dep_index):
    tree_path = list(fsentence.leaf_treeposition(dep_index - 1))
    return fsentence[tree_path[:-1]]


def filter_by_gov(dependencies, gov):
    gov_list = [gov] if isinstance(gov, int) else [gov.f_word_index, gov.f_copIndex]
    deps = [dep for dep in dependencies
            if dep['governor'] in gov_list]
    return deps


def get_full_phrase_tree(tree_node, label_type):
    node = tree_node
    while node and node.label() != label_type and node.label()[0] != "W":
        node = node.parent()

    return node


def get_full_phrase(tree_node, label_type):
    tree = get_full_phrase_tree(tree_node, label_type)
    return " ".join(tree.leaves())


def find_in_tree(tree, label, exclude):
    result = []
    if tree.label() == label:
        result.append(tree)
    if len(result) == 0:
        for child in list(tree):
            if not isinstance(child, str) and child.label() not in exclude:
                result.extend(find_in_tree(child, label, exclude))

    return result


def specifier_contains(specifiers, obj):
    for spec in specifiers:
        if spec.f_object:
            if spec.f_object == obj or specifier_contains(spec.f_object.f_specifiers, obj):
                return True

    return False


def get_action(actions, obj):
    if isinstance(obj, Action):
        return obj

    for action in actions:
        if specifier_contains(action.f_specifiers, obj):
            return action
        if action.f_actorFrom:
            cmp_obj = action.f_actorFrom
            if obj == cmp_obj or specifier_contains(cmp_obj.f_specifiers, obj):
                return action
        if action.f_object:
            cmp_obj = action.f_object
            if obj == cmp_obj or specifier_contains(cmp_obj.f_specifiers, obj):
                return action
        if action.f_xcomp:
            if specifier_contains(action.f_xcomp.f_specifiers, obj):
                return action
            elif action.f_xcomp.f_object:
                cmp_obj = action.f_xcomp.f_object
                if obj == cmp_obj or specifier_contains(cmp_obj.f_specifiers, obj):
                    return action

    return None


def starts_with(string_list, start):
    for string in string_list:
        if string.startswith(start):
            return True
    return False
