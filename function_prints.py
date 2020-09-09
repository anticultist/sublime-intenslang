import sublime
import sublime_plugin


class AddDebugPrintsToIntensFunctionsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view.window().active_view()
        
        function_definitions = view.find_by_selector("entity.name.function.intens")
        if not function_definitions:
            sublime.message_dialog("There are no INTENS functions defined!")
            return

        indentation         = self.indentation_str(view)
        var_types_rexpr_str = r"\b({})\b".format("|".join(self.variable_types(view)))

        for function_definition_rgn in reversed(function_definitions):
            function_name = view.substr(function_definition_rgn)
            if self.is_forward_declaration(view, function_definition_rgn.b):
                continue
            
            function_start = view.find("{", function_definition_rgn.b).b
            insert_pos     = self.end_of_variable_definition_block(view, var_types_rexpr_str, function_start)
            
            insert_str = "\n"
            if function_start != insert_pos:
                insert_str += "{}\n".format(indentation)

            insert_str += '{0}PRINT("FUNC {1}", EOLN);\n'.format(indentation, function_name)

            if function_start == insert_pos:
                insert_str += "{}\n".format(indentation)

            self.view.insert(edit, insert_pos, insert_str)


    def indentation_str(self, view):
        settings = view.settings()

        if settings.get("translate_tabs_to_spaces"):
            return " " * settings.get("tab_size")
        else:
            return "\t"


    def variable_types(self, view):
        # built-in base types
        var_types = ["CDATA", "COLOR", "COMPLEX", "INTEGER", "REAL", "STRING"]
        
        # user defined structures
        for function_definition_rgn in view.find_by_selector("entity.name.struct.intens"):
            var_types.append(view.substr(function_definition_rgn))

        return sorted(var_types)


    def is_forward_declaration(self, view, function_name_end_pos):
        next_block_start = view.find("{", function_name_end_pos)
        if next_block_start.empty():
            return True

        next_seperation = view.find("(,|;)", function_name_end_pos)
        if next_seperation.empty():
            return False

        return next_seperation.b < next_block_start.b


    def end_of_variable_definition_block(self, view, var_types_rexpr_str, function_start_pos):
        possible_function_end     = view.find("}", function_start_pos)
        possible_function_end_pos = float("inf") if possible_function_end.empty() else possible_function_end.b

        point = function_start_pos
        for _ in range(100):
            next_point = view.find(var_types_rexpr_str, point)
            if next_point.empty():
                break
            
            if next_point.b > possible_function_end_pos:
                break

            seperator_pos = view.find(";", point)
            if seperator_pos.empty():
                break

            point = seperator_pos.b

        return point
