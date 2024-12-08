#!/usr/bin/env python

import argparse
from reportlab.graphics import shapes
from reportlab.graphics.shapes import Drawing, Rect, Circle
from reportlab.lib.pagesizes import A4
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM

class PatternMaker:
    def __init__(self, cols, rows, square_size, page_width, page_height, output):
        self.cols = cols
        self.rows = rows
        self.square_size = square_size
        self.page_width = page_width
        self.page_height = page_height
        self.output = output

    def make_checkerboard_pattern(self):
        """Generate a checkerboard pattern."""
        drawing = Drawing(self.page_width, self.page_height)
        x_offset = (self.page_width - (self.cols * self.square_size)) / 2
        y_offset = (self.page_height - (self.rows * self.square_size)) / 2

        for row in range(self.rows):
            for col in range(self.cols):
                # Alternate black and white squares
                if (row + col) % 2 == 0:
                    x = x_offset + col * self.square_size
                    y = y_offset + row * self.square_size
                    rect = Rect(x, y, self.square_size, self.square_size, fillColor="black")
                    drawing.add(rect)

        return drawing

    def save_as_svg(self, drawing):
        """Save the generated pattern as an SVG file."""
        from svglib.svglib import svg2rlg  # Import svglib's svg2rlg function
        from reportlab.graphics import renderPDF

        # Save as SVG using ReportLab's render capabilities
        renderPDF.drawToFile(drawing)