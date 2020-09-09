import sublime
import sublime_plugin


class ListIntensFunctionUsageCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view.window().active_view()
        
        func_usage = {}
        for function_definition_rgn in view.find_by_selector("entity.name.function.intens"):
            func_usage[view.substr(function_definition_rgn)] = 0

        if not func_usage:
            sublime.message_dialog("There are no INTENS functions defined!")
            return

        undefined_functions = {}
        for function_usage_rgn in view.find_by_selector("variable.function.intens"):
            function_name = view.substr(function_usage_rgn)
            if function_name in func_usage:
                func_usage[function_name] += 1
            else:
                if function_name not in undefined_functions:
                    undefined_functions[function_name] = 0
                undefined_functions[function_name] += 1

        # add functions called by INTENS itself
        for function_name in ["QUIT", "INIT"]:
            if function_name not in func_usage:
                continue
            func_usage[function_name] += 1

        # create an output content
        out = ""

        unused_functions = []
        for key, value in sorted(func_usage.items(), key=lambda item: (item[1], item[0])):
            if value > 0:
                break
            unused_functions.append(key)

        if unused_functions:
            out += "Functions Without Usage (May Contain False-positives)\n"
            out += "=====================================================\n"
            for function_name in unused_functions:
                out += "{}\n".format(function_name)
                del func_usage[function_name]
            out += "\n\n"

        if func_usage:
            out += "Function Usage\n"
            out += "==============\n"
            for key, value in sorted(func_usage.items(), key=lambda item: (item[1], item[0])):
                out += "{:3}x {}\n".format(value, key)

        # display in a new tab/file
        self.view.window().new_file().insert(edit, 0, out)
