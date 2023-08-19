#%%
import os
import re
import argparse

import numpy as np
import pandas as pd


parser = argparse.ArgumentParser()
parser.add_argument("path_to_tclist", type=str, help="")
parser.add_argument("-i", "--path_to_ids", type=str, help="")
parser.add_argument("-f", "--force", action="store_true", help="")
args = parser.parse_args()


def generate_filelist_html(image_paths, names, show_years):
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Best Track Archive</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css">

        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-YL02WM0DDQ"></script>
        <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-YL02WM0DDQ');
        </script>

        <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
        <script>
            $(document).ready(function() {
                $('#search-input').on('keyup', function() {
                    var value = $(this).val().toLowerCase();
                    $('#search-results').empty();
                    if (value !== '') {
                        $('.image-link').each(function() {
                            if ($(this).text().toLowerCase().indexOf(value) > -1) {
                                $('#search-results').append('<div class="col-xxl-1 col-xl-2 col-md-3 col-sm-6 col-12"><a href="' + $(this).attr('href') + '" class="text-info">' + $(this).text() + '</a></div>');
                            }
                        });
                    }
                });
            });
        </script>
    </head>
    <body class="bg-white">
    <div class="container-fluid px-3">
        <div class="row pt-5">
            <div class="col text-center">
                <p class="lead mb-2" style="color: #0a2f35;">Best Track Archive</p>
                <span class="badge bg-danger text-light px-2 py-1">beta</span>
            </div>
        </div>
    </div>
    <div class="row mt-3 mx-5">
        <div class="col text-center">
            <input type="text" id="search-input" class="form-control" placeholder="Search...">
        </div>
    </div>
    <div class="row mt-3 mb-3 mx-5" id="search-results">
    </div>
    '''

    basins = ["AL","EP","WP","IO","SH"]
    for year in show_years:
        basinwise_URLs = {"AL":[], "EP":[], "WP":[], "IO":[], "SH":[]}
        basinwise_names = {"AL":[], "EP":[], "WP":[], "IO":[], "SH":[]}
        for image_path, name in zip(image_paths, names):
            bbnnyyyy = os.path.basename(image_path)[:8]
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
                bbnnyyyy = os.path.basename(image_path)[:8]
                html += f'    <a href="{bbnnyyyy[-4:]}/{bbnnyyyy}/index.html" class="text-info fs-6 image-link">{bbnnyyyy} / {name}</a>\n<br>\n'
            html += '</div>\n'
        html += '</div>\n'
        html += '</>\n'
    html += '</div>\n'
    html += '''
    <footer class="footer">
    <div class="text-center mt-4 py-4 bg-light border-top border-bottom">
        <a href="../index.html" class="text-muted align-middle">&copy; Vortex Vision</a>
    </div>
    </footer>
    </body>
    </html>
    '''
    return html

# %%
def generate_image_viewer_html(image_paths, names):
    top_img_path = image_paths[0]
    top_name = names[0]
    html = '''
    <html>
    <head>
        <title>Simple Image Viewer</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">

    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-YL02WM0DDQ"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-YL02WM0DDQ');
    </script>
    </head>
    '''

    html += f'''
    <body class="bg-white">
        <div class="container-fluid px-3">
            <div class="row pt-3">
                <div class="col text-center my-3">
                    <p class="lead mb-2" style="color: #0a2f35;">Simple Image Viewer</p>
                    <span class="badge bg-danger text-light px-2 py-1">beta</span>
                </div>
            </div>
            <div class="row mt-2">
                <div class="col-md-4 col-sm-5 col-6 form-group px-5 ml-auto">
                    <select id="image-select" class="form-control" onchange="displayImage()">
                        <option value="{top_img_path}">{os.path.basename(top_img_path)[:8]} / {top_name}</option>
    '''
    for path, name in zip(image_paths[1:], names[1:]):
        html += f'<option value="{path}">{os.path.basename(path)[:8]} / {name}</option>'
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
    <footer class="footer">
    <div class="text-center mt-4 py-4 bg-white">
        <a href="../index.html" class="text-muted align-middle">&copy; Vortex Vision</a>
    </div>
    </footer>
    </body>
    </html>
    '''
    return html


def generate_TC_html(image_path, name):
    bbnnyyyy = os.path.basename(image_path)[:8]
    html = f'''
    <html>
    <head>
        <title>{bbnnyyyy} / {name} </title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    '''
    html += '''
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-YL02WM0DDQ"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-YL02WM0DDQ');
    </script>
    </head>
    '''

    html += f'''
    <body class="bg-white">
        <div class="container-fluid px-3">
            <div class="row pt-3">
                <div class="col text-center my-3">
                    <p class="lead mb-2" style="color: #0a2f35;">{bbnnyyyy} / {name}</p>
                    <span class="badge bg-danger text-light px-2 py-1">beta</span>
                </div>
            </div>
            <div class="row">
                <div class="col-lg-7 col-12 mx-auto" id="displayed-image-container">
                    <img id="displayed-image" class="img-fluid" src="{image_path}" alt="Intensity">
                </div>
            </div>
        </div>
    '''
    html += '''
    <footer class="footer">
    <div class="text-center mt-4 py-4 bg-white">
        <a href="../../../index.html" class="text-muted align-middle">&copy; Vortex Vision</a>
    </div>
    </footer>
    </body>
    </html>
    '''
    return html
#%%
tclist = pd.read_csv(args.path_to_tclist, index_col="ID", skipinitialspace=True).sort_values("ID")
if args.path_to_ids:
    pickup_IDs = pd.read_csv(args.path_to_ids, skipinitialspace=True)["ID"]
    tclist = tclist.loc[pickup_IDs]
image_paths = list("../data/TCs/" + tclist.index.str[-4:] + "/" + tclist.index + "/outputs/" + tclist.index+"_intensity.png")
names = tclist["name"].values.tolist()
show_years = np.arange(2023,2021-1,-1).astype(str)

# [btk_archive.html]
html_content = generate_filelist_html(image_paths, names, show_years)
with open(f"{os.environ['HOME']}/git/realtimeTC/outputs/html/btk_archive.html", "w") as file:
    file.write(html_content)


# [image_viewer.html]
path_texts = " ".join(image_paths)
pattern = r'[A-Z][A-Z][0-4][0-9](\d{4})_intensity.png'
path_years = np.array(re.findall(pattern, path_texts))

image_paths_sorted = []
names_sorted = []
for year in show_years:
    image_paths_sorted = np.r_[image_paths_sorted, np.array(image_paths)[path_years==year]]
    names_sorted = np.r_[names_sorted, np.array(names)[path_years==year]]

html_content = generate_image_viewer_html(image_paths_sorted, names_sorted)
with open(f"{os.environ['HOME']}/git/realtimeTC/outputs/html/image_viewer.html", "w") as file:
    file.write(html_content)


# [ex: WP072023.html]
for image_path, name in zip(image_paths, names):
    html_content = generate_TC_html("../../"+image_path, name)

    bbnnyyyy = os.path.basename(image_path)[:8]
    year = bbnnyyyy[-4:]
    tchtml_dir = f"{os.environ['HOME']}/git/realtimeTC/outputs/html/{year}/{bbnnyyyy}"
    os.makedirs(tchtml_dir, exist_ok=True)
    with open(f"{tchtml_dir}/index.html", "w") as file:
        file.write(html_content)
# %%
