import sublime
import sublime_plugin


class CountIntensFunctionReferencesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        func_references = {}
        for function_definition_rgn in self.view.find_by_selector("entity.name.function.intens"):
            func_references[self.view.substr(function_definition_rgn)] = 0

        if not func_references:
            sublime.message_dialog("There are no INTENS functions defined!")
            return

        undefined_functions = {}
        for function_usage_rgn in self.view.find_by_selector("variable.function.intens"):
            function_name = self.view.substr(function_usage_rgn)
            if function_name in func_references:
                func_references[function_name] += 1
            else:
                if function_name not in undefined_functions:
                    undefined_functions[function_name] = 0
                undefined_functions[function_name] += 1

        # add functions called by INTENS itself
        for function_name in ["QUIT", "INIT"]:
            if function_name not in func_references:
                continue
            func_references[function_name] += 1

        # create an output content
        out = ""

        unreferenced_functions = []
        for key, value in sorted(func_references.items(), key=lambda item: (item[1], item[0])):
            if value > 0:
                break
            unreferenced_functions.append(key)

        if unreferenced_functions:
            out += "Unreferenced Functions (May Contain False-positives)\n"
            out += "====================================================\n"
            for function_name in unreferenced_functions:
                out += "{}\n".format(function_name)
                del func_references[function_name]
            out += "\n\n"

        if func_references:
            out += "Referenced Function\n"
            out += "===================\n"
            for key, value in sorted(func_references.items(), key=lambda item: (item[1], item[0])):
                out += "{:3}x  {}\n".format(value, key)

        # display in a new tab/file
        output_view = self.view.window().new_file()
        output_view.insert(edit, 0, out)
        output_view.set_line_endings("Unix")
        output_view.assign_syntax("Packages/Markdown/Markdown.sublime-syntax")
