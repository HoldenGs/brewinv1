
from interpreterv1 import Interpreter     # imports interpreter

def main():
	# all programs will be provided to your interpreter as a python string, 
	# just as shown here.
	program_source = """
func main() {
  foo = 5 = 5;
  print("The answer is: ", 4 + inputi("enter a number: "), "!");
}
	"""
	
	interp = Interpreter(trace_output=False)
	interp.run(program_source)
 
if __name__ == "__main__":
	main()