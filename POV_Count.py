import matplotlib.pyplot as plt
from cycler import cycler
import numpy as np


class Scene:
    def __init__(self, line, full_names):
        parts = line.split(';')
        self.chapter = int(parts[0])
        self.word_count = int(parts[3])

        self.pov_char = full_names[parts[1].strip()]
        self.featured_chars = list()
        if parts[2]:
            self.featured_chars = [full_names[name.strip()] for name in parts[2].split(',')]

        self.pov_char_polyjuice = parts[1].strip() if '(' in parts[1] else self.pov_char
        self.featured_chars_polyjuice = list()
        if parts[2]:
            self.featured_chars_polyjuice = [name.strip() if '(' in name else full_names[name.strip()] for name in parts[2].split(',')]

    def get_all_chars(self, polyjuice=False, pov_only=False):
        if polyjuice:
            res = [self.pov_char_polyjuice]
            if not pov_only:
                res += self.featured_chars_polyjuice
        else:
            res = [self.pov_char]
            if not pov_only:
                res += self.featured_chars
        return res


def read_files():
    # Select files
    character_word_counts = 'POVCounts.txt'
    full_character_names = 'CharacterLookupTable.txt'

    # Read in the lookup table containing full character names
    full_names = dict()
    polyjuiced_names = list()
    with open(full_character_names) as f:
        for line in f:
            parts = line.split(';')
            full_names[parts[0].strip()] = parts[1].strip()
            if '(' in parts[0]:
                polyjuiced_names.append(parts[0].strip())

    # Read in all the word counts
    all_scenes = list()
    with open(character_word_counts) as f:
        for line in f:
            all_scenes.append(Scene(line, full_names))
    all_chars = polyjuiced_names + list(full_names.values())
    return all_chars, all_scenes


def get_top_characters(char_names, scene_list, chapters, polyjuice=False, pov_only=False, number_of_chars=10, specific_names=None):
    # Get all character counts
    char_counts = {name: 0 for name in char_names}
    for scene in scene_list:
        if scene.chapter in chapters or not chapters:
            for name in scene.get_all_chars(polyjuice, pov_only):
                char_counts[name] += scene.word_count
    other = char_counts.pop("Other")

    # Sort to find top characters
    char_list = sorted([(name, count) for name, count in char_counts.items()], reverse=True, key=lambda x: x[1])
    if specific_names:
        # Only output certain names
        for i in range(len(char_list)-1, -1, -1):
            if char_list[i][0] not in specific_names:
                other += char_list.pop(i)[1]
    else:
        # Just output top n names
        while len(char_list) > number_of_chars or char_list[-1][1] == 0:
            other += char_list.pop()[1]
    char_list.append(("Other", other))
    return char_list


def draw_pie(char_list, title):
    labels = [name for name, count in char_list]
    counts = [count for name, count in char_list]
    if len(char_list) <= 10:
        plt.rcParams["axes.prop_cycle"] = cycler('color', plt.cm.tab10(np.linspace(0, 1, len(char_list))))
    elif len(char_list) <= 20:
        plt.rcParams["axes.prop_cycle"] = cycler('color', plt.cm.tab20(np.linspace(0, 1, len(char_list))))
    else:
        plt.rcParams["axes.prop_cycle"] = cycler('color', plt.cm.jet(np.linspace(0, 1, len(char_list))))
    fig1, ax1 = plt.subplots()
    ax1.pie(counts, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    if title != "None":
        plt.title(title, size=30)
    plt.show()


def draw_bar_stacked(char_lists, x_labels, title):
    # Format data
    N = len(char_lists)
    chars = dict()
    for i in range(N):
        for name, count in char_lists[i]:
            if name not in chars:
                chars[name] = [0] * N
            chars[name][i] = count
    all_chars = list(chars.keys())

    # Plot data
    if len(all_chars) <= 10:
        plt.rcParams["axes.prop_cycle"] = cycler('color', plt.cm.tab10(np.linspace(0, 1, len(all_chars))))
    elif len(all_chars) <= 20:
        plt.rcParams["axes.prop_cycle"] = cycler('color', plt.cm.tab20(np.linspace(0, 1, len(all_chars))))
    else:
        plt.rcParams["axes.prop_cycle"] = cycler('color', plt.cm.jet(np.linspace(0, 1, len(all_chars))))
    width = 0.35
    ind = [i for i in range(N)]
    sums = [0] * N
    plots = list()
    for i in range(len(all_chars)):
        plots.append(plt.bar(ind, chars[all_chars[i]], width, bottom=sums))
        for j in range(N):
            sums[j] += chars[all_chars[i]][j]

    # Add labels
    plt.ylabel("Word Count")
    if title != "None":
        plt.title(title, size=30)
    plt.xticks(ind, x_labels)
    plt.legend((plot[0] for plot in plots), all_chars)
    plt.show()


def draw_bar(char_list, title):
    labels = [name for name, count in char_list]
    counts = [count for name, count in char_list]
    width = 0.35
    ind = [i for i in range(len(char_list))]
    fig1, ax1 = plt.subplots()
    plt.setp(ax1.get_xticklabels(), rotation=30, horizontalalignment='right')
    plt.bar(ind, counts, width)
    plt.ylabel("Word Count")
    if title != "None":
        plt.title(title, size=30)
    plt.xticks(ind, labels)
    plt.show()


if __name__ == '__main__':
    all_names, scenes = read_files()  # Get a list of all scenes
    while True:
        # Read input
        graph_type = input('Graph type (Bar/Pie/Stacked Bar): ')
        chapters_str = input('Chapters (e.g. "5", "1-4", "1,3,7"): ')
        graph_title = input('Graph title ("None" for no title): ')
        polyjuiced = input('Include polyjuiced characters? (y/n): ')
        char_type = input('POV Characters only? (y/n): ')
        char_num = int(input('Number of characters to display: '))

        # Parse chapters_str
        if '-' in chapters_str:
            first, last = chapters_str.split('-')
            chapter_nums = [i for i in range(int(first), int(last)+1)]
        elif ',' in chapters_str:
            chapter_nums = [int(num) for num in chapters_str.split(',')]
        else:
            chapter_nums = [int(chapters_str)]

        # Draw graphs
        if graph_type.lower() == 'stacked bar':
            top_chars = [name for name, count in get_top_characters(all_names, scenes, chapter_nums, polyjuiced == 'y', char_type == 'y', char_num)]
            data = [get_top_characters(all_names, scenes, [c], polyjuiced == 'y', char_type == 'y', char_num, top_chars) for c in chapter_nums]
            draw_bar_stacked(data, (str(c) for c in chapter_nums), graph_title)
        else:
            data = get_top_characters(all_names, scenes, chapter_nums, polyjuiced == 'y', char_type == 'y', char_num)
            if graph_type.lower() == 'pie':
                draw_pie(data, graph_title)
            else:
                draw_bar(data[:-1], graph_title)
