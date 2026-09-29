"""Verified repository architecture, modules, and concept anchors for pallets/flask."""
from __future__ import annotations

from typing import Any

# Verified core modules in pallets/flask with verified file paths and architectural roles
FLASK_MODULES = [
    {
        "module": "flask.app",
        "file": "flask/app.py",
        "component": "Application Kernel & WSGI Entry",
        "description": "Central Flask object. Implements the WSGI interface (wsgi_app), route registration (add_url_rule, route decorator), error handling, and request dispatching.",
        "key_symbols": ["Flask", "Flask.wsgi_app", "Flask.dispatch_request", "Flask.add_url_rule"],
    },
    {
        "module": "flask.ctx",
        "file": "flask/ctx.py",
        "component": "Context Engine & Thread Locals",
        "description": "Manages RequestContext and AppContext lifetimes. Handles context stacking, push/pop mechanics, and proxies (request, session, current_app, g).",
        "key_symbols": ["RequestContext", "AppContext", "has_request_context", "has_app_context"],
    },
    {
        "module": "flask.wrappers",
        "file": "flask/wrappers.py",
        "component": "HTTP Request / Response Abstraction",
        "description": "Extends Werkzeug Request and Response objects with Flask-specific helpers like JSON decoding, routing match references, and blueprints integration.",
        "key_symbols": ["Request", "Response"],
    },
    {
        "module": "flask.blueprints",
        "file": "flask/blueprints.py",
        "component": "Modular Routing & Composition",
        "description": "Allows breaking an application into modular sub-components. Implements deferred route registration, blueprint url prefixes, and nested subdomains.",
        "key_symbols": ["Blueprint", "BlueprintSetupState"],
    },
    {
        "module": "flask.sessions",
        "file": "flask/sessions.py",
        "component": "Session Storage & Cryptography",
        "description": "Client-side signed cookie sessions. Provides SessionInterface, SecureCookieSessionInterface, and TaggedJSONSerializer extensible serialization.",
        "key_symbols": ["SessionInterface", "SecureCookieSessionInterface", "TaggedJSONSerializer"],
    },
    {
        "module": "flask.cli",
        "file": "flask/cli.py",
        "component": "Click CLI & Dev Server Runner",
        "description": "Command-line integration based on Click. Auto-discovers Flask apps, manages FLASK_APP environment variable, and boots the development server.",
        "key_symbols": ["FlaskGroup", "AppGroup", "ScriptInfo", "run_command"],
    },
    {
        "module": "flask.templating",
        "file": "flask/templating.py",
        "component": "Jinja2 Integration & Rendering",
        "description": "Binds Jinja2 environment to application context. Implements render_template, template context processors, and template global variables.",
        "key_symbols": ["render_template", "render_template_string", "Environment"],
    },
    {
        "module": "flask.signals",
        "file": "flask/signals.py",
        "component": "Signal Pub/Sub Subsystem",
        "description": "Blinker-based event signals notifying extensions of request lifecycle events (request_started, request_finished, got_request_exception).",
        "key_symbols": ["request_started", "request_finished", "template_rendered", "got_request_exception"],
    },
    {
        "module": "flask.config",
        "file": "flask/config.py",
        "component": "Configuration Management",
        "description": "Dictionary-like configuration object supporting loading from Python files, objects, JSON, and environment variables.",
        "key_symbols": ["Config", "ConfigAttribute"],
    },
]

# Step-by-step verified Request / Data Flow through pallets/flask
FLASK_REQUEST_FLOW = [
    {
        "title": "Application Entry Point",
        "component": "WSGI Gateway",
        "file_path": "flask/app.py",
        "description": "Web server (Gunicorn, uWSGI, Werkzeug) calls Flask.wsgi_app(environ, start_response). The WSGI environment is unpacked and passed to the framework.",
    },
    {
        "title": "Context Binding",
        "component": "Context Engine",
        "file_path": "flask/ctx.py",
        "description": "A RequestContext instance is created and pushed onto the thread-local context stack (ctx.push()). request and session globals become active.",
    },
    {
        "title": "Pre-Request Hooks",
        "component": "Middleware & Interceptors",
        "file_path": "flask/app.py",
        "description": "Application and blueprint url_value_preprocessors and before_request handlers run in registration order. Any early return short-circuits execution.",
    },
    {
        "title": "Routing & Dispatch",
        "component": "URL Map & View Resolution",
        "file_path": "flask/app.py",
        "description": "The URL adapter matches the request path against the Werkzeug Map. dispatch_request() executes the target view function with extracted endpoint arguments.",
    },
    {
        "title": "Response Creation",
        "component": "Response Serialization",
        "file_path": "flask/wrappers.py",
        "description": "The view return value (string, tuple, dict, generator) is converted into a standard Response object via Flask.make_response().",
    },
    {
        "title": "Post-Request Hooks & Session",
        "component": "Session & Header Finalization",
        "file_path": "flask/sessions.py",
        "description": "after_request hooks execute in reverse order. SessionInterface saves the signed cookie or storage session to response headers.",
    },
    {
        "title": "Teardown & WSGI Return",
        "component": "Resource Clean-Up",
        "file_path": "flask/ctx.py",
        "description": "The request context is popped (ctx.pop()). teardown_request and teardown_appcontext callbacks close database connections and file descriptors before start_response returns the body iterable.",
    },
]

# Concept mappings linking general software questions back to pallets/flask
GENERAL_CONCEPT_MAP: dict[str, dict[str, Any]] = {
    "flask": {
        "concept": "Flask is a lightweight, extensible Python WSGI web application microframework created by Armin Ronacher. It is designed to make getting started quick and easy, with the ability to scale up to complex applications.",
        "how_it_works": "Flask provides core routing, request/response handling, and templating while delegating HTTP handling to Werkzeug and templating to Jinja2, keeping the core compact and pluggable.",
        "in_repository": "In pallets/flask, the entire framework core is centered around the Flask class in flask/app.py with lightweight modules for contexts (flask/ctx.py), blueprints (flask/blueprints.py), and CLI (flask/cli.py).",
        "relevant_files": ["flask/app.py", "flask/ctx.py", "flask/blueprints.py", "flask/wrappers.py"],
    },
    "wsgi": {
        "concept": "WSGI (Web Server Gateway Interface, PEP 3333) is the standard specification for universal communication between Python web applications and web servers.",
        "how_it_works": "A WSGI application is a callable object accepting two arguments: environ (a dict containing HTTP headers, path, method, and server variables) and start_response (a callback function for status and headers). It returns an iterable of byte chunks.",
        "in_repository": "In pallets/flask, Flask instances implement __call__(environ, start_response) which delegates directly to Flask.wsgi_app(environ, start_response) in flask/app.py.",
        "relevant_files": ["flask/app.py", "flask/wrappers.py"],
    },
    "request context": {
        "concept": "A Request Context keeps request-specific data (such as headers, URL parameters, form data, and active session) isolated to the current worker thread or greenlet during request execution.",
        "how_it_works": "Thread-local proxies allow view functions and utilities to import global-looking variables (like request and g) without passing the request object explicitly into every internal function.",
        "in_repository": "In pallets/flask, the RequestContext class is implemented in flask/ctx.py and pushed via ctx.push() in Flask.wsgi_app. Global proxies are defined via Werkzeug LocalProxy.",
        "relevant_files": ["flask/ctx.py", "flask/app.py", "flask/globals.py"],
    },
    "middleware": {
        "concept": "WSGI middleware is a component that sits between a web server and a web application, acting as both an application to the server and a server to the application to inspect, modify, or filter requests and responses.",
        "how_it_works": "Middleware wraps the application's callable wsgi_app, intercepting the environ dictionary before forwarding it, or altering headers and body yielded by start_response.",
        "in_repository": "In pallets/flask, custom WSGI middleware is attached by wrapping app.wsgi_app (e.g. app.wsgi_app = CustomMiddleware(app.wsgi_app)). Framework-level hooks (before_request, after_request) in flask/app.py provide higher-level middleware-like functionality.",
        "relevant_files": ["flask/app.py"],
    },
    "dependency injection": {
        "concept": "Dependency injection is a design pattern where an object receives its dependencies from external sources rather than instantiating them internally, improving modularity and testability.",
        "how_it_works": "Components rely on abstractions or inversion of control containers that inject configuration, loggers, or database handles at runtime.",
        "in_repository": "In pallets/flask, dependency injection is achieved through application context proxies (g, current_app), extension initialization methods (ext.init_app(app)), and custom test client fixtures.",
        "relevant_files": ["flask/app.py", "flask/ctx.py", "flask/testing.py"],
    },
    "blueprint": {
        "concept": "A Blueprint is a mechanism for organizing a group of related views, templates, static files, and error handlers into distinct modules that can be registered on a main application.",
        "how_it_works": "Blueprints record operations (adding routes, handlers) in a deferred queue during definition, and apply them with prefixes to the application when app.register_blueprint() is called.",
        "in_repository": "In pallets/flask, Blueprint and BlueprintSetupState are implemented in flask/blueprints.py.",
        "relevant_files": ["flask/blueprints.py", "flask/app.py"],
    },
    "routing": {
        "concept": "Routing maps incoming HTTP request paths and HTTP methods to corresponding executable controller functions or endpoints.",
        "how_it_works": "A central routing table matches URL patterns, extracts typed path parameters, and dispatches the request to the matching view handler.",
        "in_repository": "In pallets/flask, routing relies on Werkzeug's routing Map and Rule objects configured through Flask.add_url_rule() and the @app.route decorator in flask/app.py.",
        "relevant_files": ["flask/app.py", "flask/blueprints.py"],
    },
}


def find_matching_concept(query: str) -> dict[str, Any] | None:
    q = query.strip().lower()
    for key, data in GENERAL_CONCEPT_MAP.items():
        if key in q:
            return data
    # Fallback to general flask concept if query asks about flask generally
    if "flask" in q:
        return GENERAL_CONCEPT_MAP["flask"]
    return None
