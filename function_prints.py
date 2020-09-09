import sublime
import sublime_plugin


class AddDebugPrintsToIntensFunctionsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view.window().active_view()
        
        function_definitions = view.find_by_selector("entity.name.function.intens")
        if not function_definitions:
            sublime.message_dialog("There are no INTENS functions defined!")
            return

        for function_definition_rgn in reversed(function_definitions):
            function_name = view.substr(function_definition_rgn)
            find_rgn = view.find("{", function_definition_rgn.b)

            indentation = self.get_indentation(view)
            self.view.insert(edit, find_rgn.b,
                             '\n{0}PRINT("FUNC {1}", EOLN);\n{0}'.format(indentation, function_name))


    def get_indentation(self, view):
        settings = view.settings()

        if settings.get("translate_tabs_to_spaces"):
            return " " * settings.get("tab_size")
        else:
            return "\t"
