"""
Specific instantiation for the S1 visualization tool

Written by DEIMOS Space S.L. (dibb)

module s1vboa
"""
# Import python utilities
import os

# Import flask utilities
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
import jinja2

# Import vboa
import vboa

def create_app():
    """
    Create and configure an instance of vboa application.
    """
    app = vboa.create_app()

    s2vboa_templates_folder = os.path.dirname(__file__) + "/templates"

    templates_loader = jinja2.ChoiceLoader([
        jinja2.FileSystemLoader(s2vboa_templates_folder),
        app.jinja_loader
    ])
    app.jinja_loader = templates_loader
    
    return app
