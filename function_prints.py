import sublime
import sublime_plugin


class AddDebugPrintsToIntensFunctionsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        function_definitions = self.view.find_by_selector("entity.name.function.intens")
        if not function_definitions:
            sublime.message_dialog("There are no INTENS functions defined!")
            return

        indentation         = self.indentation_str()
        var_types_rexpr_str = r"\b({})\b".format("|".join(self.variable_types()))

        for function_definition_rgn in reversed(function_definitions):
            function_name = self.view.substr(function_definition_rgn)
            if self.is_forward_declaration(function_definition_rgn.b):
                continue
            
            function_start = self.view.find("{", function_definition_rgn.b).b
            insert_pos     = self.end_of_variable_definition_block(var_types_rexpr_str, function_start)
            
            insert_str = "\n"
            if function_start != insert_pos:
                insert_str += "{}\n".format(indentation)

            insert_str += '{}PRINT("FUNC {}", EOLN);\n'.format(indentation, function_name)

            if function_start == insert_pos:
                insert_str += "{}\n".format(indentation)

            self.view.insert(edit, insert_pos, insert_str)


    def indentation_str(self):
        settings = self.view.settings()

        if settings.get("translate_tabs_to_spaces"):
            return " " * settings.get("tab_size")
        else:
            return "\t"


    def variable_types(self):
        # built-in base types
        var_types = ["CDATA", "COLOR", "COMPLEX", "INTEGER", "REAL", "STRING"]
        
        # user defined structures
        for function_definition_rgn in self.view.find_by_selector("entity.name.struct.intens"):
            var_types.append(self.view.substr(function_definition_rgn))

        return sorted(var_types)


    def is_forward_declaration(self, function_name_end_pos):
        next_block_start = self.view.find("{", function_name_end_pos)
        if next_block_start.empty():
            return True

        next_seperation = self.view.find("(,|;)", function_name_end_pos)
        if next_seperation.empty():
            return False

        return next_seperation.b < next_block_start.b


    def end_of_variable_definition_block(self, var_types_rexpr_str, function_start_pos):
        possible_function_end     = self.view.find("}", function_start_pos)
        possible_function_end_pos = float("inf") if possible_function_end.empty() else possible_function_end.b

        point = function_start_pos
        for _ in range(100):
            next_point = self.view.find(var_types_rexpr_str, point)
            if next_point.empty():
                break
            
            if next_point.b > possible_function_end_pos:
                break

            seperator_pos = self.view.find(";", point)
            if seperator_pos.empty():
                break

            point = seperator_pos.b

        return point
