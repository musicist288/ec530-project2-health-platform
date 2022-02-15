#!/usr/bin/env python
#
#  This file is based on
#  https://gist.github.com/oseiskar/dbd51a3727fc96dcf5ed189fca491fb3
#
#  Copyright 2017 Otto Seiskari
#  Licensed under the Apache License, Version 2.0.
#  See http://www.apache.org/licenses/LICENSE-2.0 for the full text.
#
#  This file is based on
#  https://github.com/swagger-api/swagger-ui/blob/4f1772f6544699bc748299bd65f7ae2112777abc/dist/index.html
#  (Copyright 2017 SmartBear Software, Licensed under Apache 2.0)
#
"""
This script converts the REST API specification to a nicely formatted HTML file.
This implementation was adapted from the original in the followign ways:

    - The CLI interface takes arguments to specify and input file and output file
      rather than reading sys.stdin and printing to std.out
    - The implementation will look for redoc-cli if it is available in the users' path
      and prefer that. If it's not available, rather than making the user install redoc
      which requires nodejs, it will default to the original implementation by Otto Seiskari.

Usage:

    python openapi_to_html.py path/to/api.yaml output_file.html

"""

# flake8: noqa
# Disabling flake8 this this is software pulled from elsewhere.

import yaml
import json
import sys
import shutil
import os


TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Swagger UI</title>
  <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,700|Source+Code+Pro:300,600|Titillium+Web:400,600,700" rel="stylesheet">
  <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/swagger-ui.css" >
  <style>
    html
    {
      box-sizing: border-box;
      overflow: -moz-scrollbars-vertical;
      overflow-y: scroll;
    }
    *,
    *:before,
    *:after
    {
      box-sizing: inherit;
    }

    body {
      margin:0;
      background: #fafafa;
    }
  </style>
</head>
<body>

<div id="swagger-ui"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/swagger-ui-bundle.js"> </script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/swagger-ui-standalone-preset.js"> </script>
<script>
window.onload = function() {

  var spec = %s;

  // Build a system
  const ui = SwaggerUIBundle({
    spec: spec,
    dom_id: '#swagger-ui',
    deepLinking: true,
    presets: [
      SwaggerUIBundle.presets.apis,
      SwaggerUIStandalonePreset
    ],
    plugins: [
      SwaggerUIBundle.plugins.DownloadUrl
    ],
    layout: "StandaloneLayout"
  })

  window.ui = ui
}
</script>
</body>

</html>
"""

def cli_main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} input_file output_file", file=sys.stderr)
        sys.exit(-1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    redoccli = shutil.which("redoc-cli")
    with open(input_file) as handle:
        spec = yaml.load(handle.read(), Loader=yaml.FullLoader)

    if redoccli:
        print("Rendering document using redoc-cli")
        os.system(f"{redoccli} bundle -o {output_file} {input_file}")
    else:
        print("Rendering document using swagger formatting")
        with open(output_file, "w") as handle:
            handle.write(TEMPLATE % json.dumps(spec))


if __name__ == "__main__":
    cli_main()
