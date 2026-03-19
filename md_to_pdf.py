#!/usr/bin/env python3
import os
import click
from utils.pdf import convert as md_to_pdf

@click.command()
@click.argument('md_files', nargs=-1, type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='output', help='Directory to save the PDF files.')
def main(md_files, output_dir):
    """
    Convert specified markdown files to PDF format and save them in the output directory.
    """
    if not md_files:
        click.echo("❌ No markdown files specified. Please provide at least one MD file.")
        return

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        click.echo(f"📁 Created output directory: {output_dir}")

    for md_file in md_files:
        if not md_file.endswith('.md'):
            click.echo(f"⚠️  Skipping {md_file}: Not a markdown file.")
            continue

        filename = os.path.basename(md_file)
        pdf_filename = filename.replace('.md', '.pdf')
        pdf_path = os.path.join(output_dir, pdf_filename)

        click.echo(f"⏳ Converting {filename} to PDF...")
        try:
            md_to_pdf(md_file, pdf_path)
            # md_to_pdf in utils/pdf already prints a success message, 
            # but we can add more context if needed.
        except Exception as e:
            click.echo(f"❌ Failed to convert {md_file}: {e}")

if __name__ == "__main__":
    main()
