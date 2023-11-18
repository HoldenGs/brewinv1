from brewparse import parse_program
from intbase import InterpreterBase
from element import Element
from intbase import ErrorType


class Interpreter(InterpreterBase):
	ast = None
	variables = {}
	functions = {}
	frames = []

	def __init__(self, console_output=True, inp=None, trace_output=False):
		super().__init__(console_output, inp)
		self.trace_output = trace_output
  
	def run(self, program):
		self.ast = parse_program(program)
  
		if self.ast.get("functions") == None:
			super().error(ErrorType.FAULT_ERROR, "No functions found")

		self.functions = self.ast.get("functions")
		if self.trace_output:
			print("Functions:")
			for func in self.functions:
				print(func)
  
		for func in self.functions:
			if func.get("name") == "main":
				if self.trace_output:
					print("Running main entrypoint")
				return self.run_function(func)

		super().error(ErrorType.NAME_ERROR, "No main function found")

	def run_function(self, function_node):
		if self.trace_output:
			print("Running function: {}".format(function_node.get("name")))
   
		f_name = function_node.get("name")
		args = function_node.get("args")

		if f_name == "inputi":
			if len(args) > 1:
				super().error(ErrorType.NAME_ERROR, f"No inputi() function found that takes > 1 parameter")
			elif len(args) == 1:
				super().output(self.evaluate_expression(args[0]).get("val"))
	
			return Element(InterpreterBase.INT_DEF, val=int(super().get_input()))
		elif f_name == "print":
			self.print(args)
		elif f_name == "main":
			self.frames.append({function_node.get("name"): args})
			for statement_node in function_node.get("statements"):
				self.run_statement(statement_node)
		else:
			super().error(ErrorType.NAME_ERROR, f"Unknown Function Referenced")

	def run_statement(self, statement_node):
		if statement_node.elem_type == "=":
			self.run_assignment(statement_node)
		elif statement_node.elem_type == InterpreterBase.FCALL_DEF:
			self.run_function(statement_node)

	def run_assignment(self, statement_node):
		expression_node = statement_node.get("expression")
		var_name = statement_node.get("name")

		if expression_node.elem_type in ["+", "-", "*", "/"]:
			val = self.evaluate_expression(expression_node)
			self.variables[var_name] = val
		elif expression_node.elem_type in [InterpreterBase.INT_DEF, InterpreterBase.STRING_DEF]:
			self.variables[var_name] = expression_node
		elif expression_node.elem_type == "fcall":
			self.variables[var_name] = self.run_function(expression_node)
		elif expression_node.elem_type == "var":
			self.variables[var_name] = self.evaluate_expression(expression_node)
		else:
			super().error(ErrorType.TYPE_ERROR, f"Invalid assignment: {expression_node.elem_type}")

	def print(self, args):
		eval_args = [self.evaluate_expression(arg) for arg in args]
		string_args = [str(arg.get("val")) for arg in eval_args]
		super().output(''.join(string_args))

	def evaluate_expression(self, expression_node):
		if expression_node.elem_type == "fcall":
			return self.run_function(expression_node)
		elif expression_node.elem_type == "var":
			var = expression_node.get("name")
			if var in self.variables:
				return self.variables[var]
			else:
				super().error(ErrorType.NAME_ERROR, "Unknown variable: {}".format(var))
		elif expression_node.elem_type == "int":
			return Element(InterpreterBase.INT_DEF, val=expression_node.get("val"))
		elif expression_node.elem_type == "string":
			return Element(InterpreterBase.STRING_DEF, val=expression_node.get("val"))
		elif expression_node.elem_type in ["+", "-"]:
			op1 = self.evaluate_expression(expression_node.get("op1"))
			op2 = self.evaluate_expression(expression_node.get("op2"))
			if op1.elem_type != op2.elem_type:
				super().error(ErrorType.TYPE_ERROR, "Type mismatch on binary operation between {} and {}: {} {} {}".format(op1.elem_type, op2.elem_type, op1.get("val"), expression_node.elem_type, op2.get("val")))
			if expression_node.elem_type == "+":
				sum = op1.get("val") + op2.get("val")
				return Element(InterpreterBase.INT_DEF, val=sum)
			else:
				diff = op1.get("val") - op2.get("val")
				return Element(InterpreterBase.INT_DEF, val=diff)
		else:
			super().error(ErrorType.TYPE_ERROR, "Unknown expression type: {}".format(expression_node.elem_type))

