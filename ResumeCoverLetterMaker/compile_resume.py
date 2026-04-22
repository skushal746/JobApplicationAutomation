import os
import sys
from utils.latex import compile_tex_to_pdf

def main():
    # Default paths
    input_file = "assets/KushalSharma_Resume.tex"
    output_dir = "output"
    
    # Allow overriding via command line
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]

    if not os.path.exists(input_file):
        print(f"Error: LaTeX file not found at {input_file}")
        print(f"Please place your LaTeX resume at assets/KushalSharma_Resume.tex")
        sys.exit(1)

    try:
        pdf_path = compile_tex_to_pdf(input_file, output_dir)
        print(f"\nSuccess! Your PDF is ready at: {pdf_path}")
    except Exception as e:
        print(f"\nFailed to compile LaTeX: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure MacTeX is finished installing.")
        print("2. Try running 'pdflatex --version' in your terminal.")
        print("3. Check the LaTeX file for syntax errors.")
        sys.exit(1)

if __name__ == "__main__":
    main()
