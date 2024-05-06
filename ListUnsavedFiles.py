import re

import sublime
import sublime_plugin

RESULTS_VIEW = "Unsaved Files"

NO_RESULTS = "No unsaved files found"


def find_view_by_name(window, name):
    """
    finds a view whose filename or name matches passed-in name
    """
    results = [v for v in window.views() if v.file_name() == name or v.name() == name]
    if len(results) > 0:
        return results[0]
    return None


def find_view_by_id(window, _id):
    results = [v for v in window.views() if v.id() == _id]
    if len(results) > 0:
        return results[0]
    return None


class ListUnsavedFiles(sublime_plugin.WindowCommand):
    """
    Command that opens a new scratch view containing a list of clickable unsaved files
    """

    def run_(self, edit_token, args):
        window = sublime.active_window()

        dirty = []
        for view in window.views():
            if not view.is_scratch() and view.is_dirty():
                dirty.append(view)

        output = "Unsaved files\n\n"
        if dirty:
            for dirty_item in dirty:
                name = dirty_item.file_name()
                if not name:
                    name = dirty_item.name() or "Untitled"
                    name = name + " (non-file view id: {})".format(dirty_item.id())

                output += "{}\n".format(name)
        else:
            output += NO_RESULTS

        existing_view = find_view_by_name(window, RESULTS_VIEW)
        if existing_view:
            existing_view.close()

        output_view = window.new_file()
        output_view.set_name(RESULTS_VIEW)
        output_view.set_scratch(True)

        edit = output_view.begin_edit(edit_token, "")
        output_view.insert(edit, 0, output)
        output_view.end_edit(edit)

        window.focus_view(output_view)


class UnsavedFilesResultsListener(sublime_plugin.EventListener):
    """
    Listener for click events inside the results view
    """

    def on_text_command(self, view, command, args):
        if view.name() == RESULTS_VIEW:
            if command == "drag_select":
                window = view.window()
                event = args["event"]
                # double click
                if args.get('by') == 'words':
                    point = view.window_to_text((event["x"], event["y"]))
                    line = view.substr(view.line(point))
                    if line != NO_RESULTS:
                        match = re.search(r"view id: (\d+)", line)
                        if match:
                            view_id = int(match.group(1))
                            target_view = find_view_by_id(window, view_id)
                        else:
                            target_view = find_view_by_name(window, line)

                        if target_view:
                            window.focus_view(target_view)
