        def insert_paragraph_after(reference_para, text, parent_element):
            """Insert a new paragraph after reference, copying its formatting and supporting rich text."""
            # Create new paragraph (empty for now)
            new_para = parent_element.add_paragraph()

            # Copy paragraph-level formatting
            if reference_para.style:
                new_para.style = reference_para.style
            new_para.alignment = reference_para.alignment

            # Copy paragraph format
            pf_src = reference_para.paragraph_format
            pf_dst = new_para.paragraph_format
            pf_dst.left_indent = pf_src.left_indent
            pf_dst.right_indent = pf_src.right_indent
            pf_dst.first_line_indent = pf_src.first_line_indent
            pf_dst.space_before = pf_src.space_before
            pf_dst.space_after = pf_src.space_after
            pf_dst.line_spacing = pf_src.line_spacing

            # Get base run for formatting
            base_run = reference_para.runs[0] if reference_para.runs else None

            # Parse and apply rich text
            text_parts = parse_rich_text(text)
            apply_rich_text_to_paragraph(new_para, text_parts, base_run)

            # Move it to the right position in XML
            new_para._element.getparent().remove(new_para._element)
            reference_para._element.addnext(new_para._element)

            return new_para
