"""
Specific instantiation for the S1 visualization tool

Written by DEIMOS Space S.L. (dibb)

module s1vboa
"""
# Import python utilities
import os

# Import flask utilities
from flask import Flask, send_from_directory
from flask_debugtoolbar import DebugToolbarExtension
import jinja2

# Import vboa
import vboa
from s1vboa.views.dhus_completeness import dhus_completeness

def create_app():
    """
    Create and configure an instance of vboa application.
    """
    app = vboa.create_app()

    # Register the specific views
    app.register_blueprint(dhus_completeness.bp)
    
    # Register the specific templates folder
    s2vboa_templates_folder = os.path.dirname(__file__) + "/templates"
    templates_loader = jinja2.ChoiceLoader([
        jinja2.FileSystemLoader(s2vboa_templates_folder),
        app.jinja_loader
    ])
    app.jinja_loader = templates_loader

    # Register the specific static folder
    s1vboa_static_folder = os.path.dirname(__file__) + "/static"
    @app.route('/s1_static_images/<path:filename>')
    def s1_static(filename):
        return send_from_directory(s1vboa_static_folder + "/images", filename)
    # end def
    
    return app
