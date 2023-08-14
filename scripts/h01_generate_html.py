#%%
import os
import re
import glob

import numpy as np
import pandas as pd


def generate_filelist_html(image_paths, name):
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <title>Best Track Archive</title>
      <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css">
    </head>
    <body class="bg-white">
    <div class="container-fluid px-3">
        <div class="row pt-5">
            <div class="col text-center">
            <p class="h3" style="color: #252e4b;">Best Track Archive</p>
            <!-- <span class="badge bg-danger text-light px-2 py-1">TEST</span> -->
            <div class="alert alert-warning mt-3 mx-5 px-5" role="alert">
                This is an archive of the preliminary TC analysis from JTWC and NHC
            </div>
        </div>
    </div>
    '''
    basins = ["AL","EP","WP","IO","SH"]
    for year in years:
        basinwise_URLs = {"AL":[], "EP":[], "WP":[], "IO":[], "SH":[]}
        basinwise_names = {"AL":[], "EP":[], "WP":[], "IO":[], "SH":[]}
        for image_path, name in zip(image_paths, names):
            bbnnyyyy = os.path.basename(image_path)[:-4]
            if bbnnyyyy[-4:] == year:
                basinwise_URLs[bbnnyyyy[:2]].append(image_path)
                basinwise_names[bbnnyyyy[:2]].append(name)

        html += f'<div class="row mt-3 py-1 mx-auto border-top border-bottom bg-light">\n'
        html += f'<div class="col text-center">\n'
        html += f'<p class="h5 text-center mt-2" style="color: #252e4b;">{year}</p>\n'
        html += '</div>\n'
        html += '</div>\n'
        html += '<div class="row">\n'
        for basin in basins:
            html += f'<div class="col-xl-2 col-md-4 col-sm-6 col-12 mt-2 mx-auto mb-3 text-center">\n'
            html += f'<p class="h6 text-body">{basin}</p>\n'
            for image_path, name in zip(basinwise_URLs[basin], basinwise_names[basin]):
                bbnnyyyy = os.path.basename(image_path)[:-4]
                html += f'    <a href="{image_path}" class="text-info fs-6">{bbnnyyyy} / {name}</a>\n<br>\n'
            html += '</div>\n'
        html += '</div>\n'
        html += '</>\n'
    html += '</div>\n'
    html += '''
    <footer class="footer">
    <div class="text-center mt-4 py-4 bg-light border-top">
        <span class="text-muted align-middle">&copy; TC Times</span>
    </div>
    </footer>

    </body>
    </html>
    '''
    return html

tclist = pd.read_csv("/Users/tsukada/git/realtimeTC/refdata/TCs/tclist.csv", skipinitialspace=True)
tclist = tclist.sort_values("ID")
image_paths = list("tmp/" + tclist["ID"] + ".png")
names = tclist["name"].values.tolist()

years = np.arange(2023,2021-1,-1).astype(str)
html_content = generate_filelist_html(image_paths, names)

with open("/Users/tsukada/git/realtimeTC/outputs/html/file_list.html", "w") as file:
    file.write(html_content)

# %%
def generate_image_viewer_html(image_paths, names):
    top_img_path = image_paths[0]
    top_name = names[0]
    html = f'''
    <html>
    <head>
        <title>Simple Image Viewer</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    </head>
    <body class="bg-white">
        <div class="container-fluid px-3">
            <div class="row pt-3">
                <div class="col text-center">
                    <p class="h4 text-center my-3">Simple Image Viewer</p>
                </div>
            </div>
            <div class="row mt-1">
                <div class="col-10 mx-auto alert alert-warning text-center" role="alert">
                    This is an archive of the preliminary TC analysis from JTWC and NHC
                </div>
            </div>
            <div class="row mt-2">
                <div class="col-md-4 col-sm-5 col-6 form-group px-5 ml-auto">
                    <select id="image-select" class="form-control" onchange="displayImage()">
                        <option value="{top_img_path}">{os.path.basename(top_img_path)[:-4]} / {top_name}</option>
    '''
    for path, name in zip(image_paths[1:], names[1:]):
        html += f'<option value="{path}">{os.path.basename(path)[:-4]} / {name}</option>'

    html += f'''
                    </select>
                </div>
            </div>
            <div class="row">
                <div class="col-lg-6 col-12 mx-auto" id="displayed-image-container">
                    <img id="displayed-image" class="img-fluid" src="{top_img_path}" alt="Selected Image">
                </div>
            </div>
        </div>
        '''
    html += '''        
        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
        <script>
            function displayImage() {
                var selectedImage = document.getElementById("image-select").value;
                var displayedImage = document.getElementById("displayed-image");
                displayedImage.src = selectedImage;
            }
        </script>
    </body>
    </html>
    '''

    return html

path_texts = " ".join(image_paths)
pattern = r'[A-Z][A-Z][0-4][0-9](\d{4}).png'
path_years = np.array(re.findall(pattern, path_texts))

image_paths_sorted = []
names_sorted = []
for year in years:
    image_paths_sorted = np.r_[image_paths_sorted, np.array(image_paths)[path_years==year]]
    names_sorted = np.r_[names_sorted, np.array(names)[path_years==year]]

html_content = generate_image_viewer_html(image_paths_sorted, names_sorted)
with open("/Users/tsukada/git/realtimeTC/outputs/html/image_viewer.html", "w") as file:
    file.write(html_content)

# %%
