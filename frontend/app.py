import os
from flask import Flask, request, render_template

from frontend_app.utils.common import get_response, render_response


app = Flask(__name__)

TEMPLATE_NAME = "form.html"


@app.route("/transform", methods=["GET", "POST"])
def transform_image():

    if request.method == "GET":
        form_data = {
            "prompt": "",
            "num_inference_steps": "10",
            "image_guidance_scale": "1",
        }
        return render_template(TEMPLATE_NAME, form_data=form_data)

    response, original_image, form_data = get_response(request)

    return render_response(
        response=response,
        original_image=original_image,
        template_name=TEMPLATE_NAME,
        form_data=form_data,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT_NUMBER", 5000))
