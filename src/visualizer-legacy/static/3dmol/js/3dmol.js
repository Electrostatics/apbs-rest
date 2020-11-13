/* 3Dmol functions 
*
*
*/

   //protein object
   var protein = {
    surface: $3Dmol.SurfaceType.SAS,
    opacity: 1,
    min_isoval: -5,
    max_isoval: 5,
    colorScheme: "RWB",
    volumedata: null
};

var volumedata = null;
var glviewer = null;
var labels = [];


var addLabels = function() {
    var atoms = glviewer.getModel().selectedAtoms({
        atom : "CA"
    });
    for ( var a in atoms) {
        var atom = atoms[a];

        var l = glviewer.addLabel(atom.resn + " " + atom.resi, {
            inFront : true,
            fontSize : 12,
            position : {
                x : atom.x,
                y : atom.y,
                z : atom.z
            }
        });
        atom.label = l;
        labels.push(atom);
    }
};

var removetheLabels = function() {
    for (var i = 0; i < labels.length; i++) {
    var atom = labels[i]
    glviewer.removeLabel(atom.label)
    delete atom.label
    }
    //console.log(labels)
    
    labels = []

    };

/* removed until remove functionality works -- also see addpqr
var atomcallback = function(atom, viewer) {
    if (atom.clickLabel === undefined
            || !atom.clickLabel instanceof $3Dmol.Label) {
        atom.clickLabel = viewer.addLabel(atom.elem + atom.serial, {
            fontSize : 14,
            position : {
                x : atom.x,
                y : atom.y,
                z : atom.z
            },
            backgroundColor: "gray"
        });
        atom.clicked = true;
    }

    //toggle label style
    else {

        //if (atom.clicked) {
        //  var newstyle = atom.clickLabel.getStyle();
        //  newstyle.backgroundColor = 0x66ccff;

        //  viewer.setLabelStyle(atom.clickLabel, newstyle);
        //  atom.clicked = !atom.clicked;
        //}
        if (atom.clicked) {
            viewer.removeLabel(atom.clickLabel);
            delete atom.clickLabel;
            atom.clicked = false;
        }

    }
};
*/
var glviewer;
$(document).ready(function() {
    glviewer = $3Dmol.createViewer("gldiv", {
    defaultcolors : $3Dmol.rasmolElementColors
    });
    glviewer.setBackgroundColor("black");

});

var fileselected = function(files, func){
    
    
    readText(files, func);

    
};
 
var addpqr = function(data){
    
    //moldata = data = $("#moldata_pdb_large").val();
    //console.log(data); //see contents of file
    receptorModel = m = glviewer.addModel(data, "pqr");

    atoms = m.selectedAtoms({});

    /* removed until remove atom functionality is fixed
    for ( var i in atoms) {
        var atom = atoms[i];
        atom.clickable = true;
        atom.callback = atomcallback;
    }
    */
    glviewer.mapAtomProperties($3Dmol.applyPartialCharges);
    glviewer.zoomTo();
    glviewer.render();
    
    };
    
    
var addcube = function (volumedata){
    //protein.volumedata = volumedata;
    window.volumedata = new $3Dmol.VolumeData(volumedata, "cube");
    //volumedata = $("#volumetric_data").val();
    //glviewer.addIsosurface(volumedata, {isoval: -5, color:"red", smoothness: 10})
    //glviewer.addIsosurface(volumedata, {isoval: 5, color:"blue", smoothness: 1})
    
    
    glviewer.render();
    create_surface();
    };

var backbone = function (){
    var atoms = glviewer.getModel().selectedAtoms({
        });
    for ( var i = 0; i < atoms.length; i++) {
        var atom = atoms[i];
    if (atom.atom == "H")
    //    delete atom
    //if (atom == "O")
    //    delete atom
    //if (atom.atom == "CA")
    atoms.splice(i,1);
    }
}

var readText = function(input,func) {
    
    if(input.length > 0) {
        var file = input[0];
        var reader = new FileReader();
        reader.onload = function(evt) {
            func(evt.target.result,file.name);
        };
        reader.readAsText(file); //needs to be type Blob
        $(input).val('');
        
    }

};

var distance = function(atom1, atom2) {
    m = glviewer.getModel(0);
    myatoms = m.selectedAtoms({});
    //console.log(myatoms)
    for ( var i in myatoms) {
    var myatom = myatoms[i];
    myatom.clickable = true;
}   
    myatom.onclick = console.log(myatom)
};

/*update surface based on selected action 
* 0 -  
* 1 - change surface
* 2 - set translucent
* 3 - set opaque
*/
function update_surface(action){
    var e = document.getElementById("selected_surface");
    var x = e.options[e.selectedIndex].value;
    glviewer.removeSurface(surf);
    switch (action){
        case 1:
            if (x == 'SAS')
               protein.surface = $3Dmol.SurfaceType.SAS;
            else if (x == 'SES')
                protein.surface = $3Dmol.SurfaceType.SES;
            else if (x == 'VDW')
                protein.surface = $3Dmol.SurfaceType.VDW;
            break;
        case 2:
            protein.opacity = 0.70;
            break;
        case 3: 
            protein.opacity = 1;
            break;
        case 4:
            protein.min_isoval = -5;
            protein.max_isoval = 5;
            break;
        
        default:
            break;
    }
        set_color();
    }

    function show_colorbar(){
        var w = document.getElementById("selected_scheme");
        var y = w.options[w.selectedIndex].value;
        //console.log(y);
        if(y=='RWB')
           document.getElementById("colorbar").innerHTML ="<img src=/viz/static/3dmol/images/rwb.png width='250'>";
        if(y=='RGB')
            document.getElementById("colorbar").innerHTML ="<img src=/viz/static/3dmol/images/rgb.png width='250'>";

    }

    function surface_vis(checkbox){
        //console.log(here);
        if(checkbox.checked)
            on_surface();
        else
            glviewer.removeSurface(surf);
    }

    function surface_opacity(checkbox){
        //console.log(here);
        if(checkbox.checked)
            update_surface(3);
        else
            update_surface(2);
    }

    function surface_labels(checkbox){
        //console.log(here);
        if(checkbox.checked){
            removetheLabels(glviewer);
            glviewer.render();
        }
        else{
            addLabels(glviewer); 
            glviewer.render();
        }
    }

    function set_vis(){
        var f = document.getElementById("selected_vis");
        var y = f.options[f.selectedIndex].value;
        vis=y;

        if(y=="stick"){ glviewer.setStyle({},{stick:{}}); glviewer.render();}
        if(y=="line"){glviewer.setStyle({},{line:{}}); glviewer.render();}
        if(y=="cross"){glviewer.setStyle({},{cross:{linewidth:5}}); glviewer.render();}
        if(y=="sphere"){glviewer.setStyle({},{sphere:{}}); glviewer.render();}
        if(y=="cartoon"){glviewer.setStyle({hetflag:false},{cartoon:{color: 'spectrum'}}); glviewer.render();}
    }

    function set_color(){
    //inefficient -- need to fix!
    //want to set as protein attribute
    var f = document.getElementById("selected_scheme");
    var y = f.options[f.selectedIndex].value;
    protein.colorScheme=y;
    
    if(protein.colorScheme=="RWB")
        volscheme_to_use = new $3Dmol.Gradient.RWB(protein.min_isoval,protein.max_isoval);
    else if(protein.colorScheme=="RGB")
        volscheme_to_use = new $3Dmol.Gradient.ROYGB(protein.min_isoval,protein.max_isoval);
    else if(protein.colorScheme=="BWR")
        volscheme_to_use = new $3Dmol.Gradient.Sinebow(protein.min_isoval,protein.max_isoval);
    
    surf = glviewer.addSurface(protein.surface, {opacity:protein.opacity, voldata: volumedata, volscheme: volscheme_to_use});
    }
    
    //starts program with SAS surface
    function create_surface(){
        volscheme_to_use = new $3Dmol.Gradient.RWB(protein.min_isoval,protein.max_isoval);
        surf = glviewer.addSurface(protein.surface, {opacity:protein.opacity, voldata: volumedata, volscheme: volscheme_to_use});
    }

    //Turn on the surface for the current selected surface
    function on_surface(){
        var e = document.getElementById("selected_surface");
        var x = e.options[e.selectedIndex].value;
        if (x == 'SAS')
            protein.surface = $3Dmol.SurfaceType.SAS;
        else if (x == 'SES')
            protein.surface = $3Dmol.SurfaceType.SES;
        else if (x == 'VDW')
            protein.surface = $3Dmol.SurfaceType.VDW;

        set_color();
    }

    //change output for min_isoval range
    function set_min_isoval(min_val) {
        document.querySelector('#min_isoval').value = min_val;
        protein.min_isoval = min_val;
        update_surface(0);
    }

    //change output for max_isoval range
    function set_max_isoval(max_val) {
        document.querySelector('#max_isoval').value = max_val; 
        protein.max_isoval = max_val;
        update_surface(0);
    }

    //reset min and max isovals
    function reset_vals() {
        set_min_isoval2(-5);
        set_max_isoval2(5);
        document.getElementById("min_isoval2").value = "-5";
        document.getElementById("max_isoval2").value = "5";
        update_surface(0);
        return false;
    }
    
//change output for min_isoval range, not perfect
    function set_min_isoval2(min_val) {
        document.getElementById("min_isoval").innerHTML = min_val;
        protein.min_isoval = Number(min_val);
        console.log(document.getElementById('min_isoval').value);
        update_surface(0);
    }

    //change output for max_isoval range, not perfect
    function set_max_isoval2(max_val) {
        document.getElementById("max_isoval").innerHTML = max_val;
        protein.max_isoval = Number(max_val);
        update_surface(0);
    }

    function getpqr(jobid, pqr_prefix, storage_url){
        var xhr = new XMLHttpRequest();
        //jobid = 14357857643;
        url = storage_url+"/"+jobid+"/"+pqr_prefix+".pqr";
        // console.log(url)
        // url = "http://nbcr-222.ucsd.edu/pdb2pqr_2.1.1/tmp/"+jobid+"/"+jobid+".pqr";
        //url = "../3dmol/files/1fas.pqr";
        xhr.open("GET", url);
        //xhr.responseType = 'blob';

        xhr.onload = function(e) {
          if (this.status == 200) {
            // Note: .response instead of .responseText
            //var blob = new Blob([this.response], {type: 'text/plain'});
           //readText(this.response);
           addpqr(this.response);
          }
          
        };
        xhr.send(null);
        
    }

    function getcube(jobid, pqr_prefix, storage_url){
        var xhr = new XMLHttpRequest();
        xhr.open("GET", storage_url+"/"+jobid+"/"+pqr_prefix+".cube");
        // console.log(storage_url+"/"+jobid+"/"+jobid+".cube")
        // xhr.open("GET", "http://nbcr-222.ucsd.edu/pdb2pqr_2.1.1/tmp/"+jobid+"/"+jobid+".cube");
        //xhr.open("GET", "../3dmol/files/1fas.cube");
        //xhr.responseType = 'blob';

        xhr.onload = function(e) {
          if (this.status == 200) {
            // Note: .response instead of .responseText
            //var blob = new Blob([this.response], {type: 'text/plain'});
           //readText(this.response);
           addcube(this.response);
          }
          
        };
        xhr.send(null);
        
    }

var surfaceOn = true
function toggleSurface(){
    if(surfaceOn){
        surfaceOn = false
        on_surface()
    }
    else{
        surfaceOn = true
        glviewer.removeSurface(surf)
    }
}

var surfaceOpacity = true
function toggleOpacity(){
    if(surfaceOpacity){
        update_surface(3)
        surfaceOpacity = false
    }
    else{
        update_surface(2)
        surfaceOpacity = true
    }
}

var modelLabels = false
function toggleLabels(){
    if(modelLabels){
        removetheLabels(glviewer);
        glviewer.render();
        modelLabels = false
    }
    else{
        addLabels(glviewer);
        glviewer.render();
        modelLabels = true
    }
}

// Adapted from the savePng function from new versions of 3Dmol
var savePng = function() {
    // Get query string params
    let querystring_params = (new URL(document.location)).searchParams
    let job_id = querystring_params.get('jobid')
    let pqr_name = querystring_params.get('pqr')

    // Retrieve 3Dmol canvas data from GLViewer
    let filename = `${job_id}_3dmol.png`;
    let text = glviewer.pngURI();
    let ImgData = text;

    // Create anchor element from which to download image
    let link = document.createElement('a');
    link.href = ImgData;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Callback function for adjusting transparency slider
var adjustBackgroundTransparency = function(alpha_val) {
    document.getElementById("bg_alpha_val").innerHTML = alpha_val;
    glviewer.setBackgroundColor('black', 1-(alpha_val/100))
    glviewer.render()
}

// Adjust export button text
var renderExportButtonText = function(select_val) {
    console.log('function:   renderExportButtonText()')
    console.log(`select_val: ${select_val}`)
    console.log(`val jquery: ${ $("#select_export_type").val() }`)

    // Extract text from selected export type
    // let export_text = $("#select_export_type option:selected").text().trim()
    // $("#export-button").val( `Export as ${export_text}` )

    // Show opacity slider if exporting to PNG
    if( select_val === "png" ){ showTransparancySlider(true) }
    else{ showTransparancySlider(false) }

    // Set export function corresponding to export type
    if( select_val === "png" )
        $("#export-button").attr("onclick", "savePng()")

    else if( select_val === "pymol" )
        $("#export-button").attr("onclick", "savePymol()")

    else if( select_val === "unitymol" )
        $("#export-button").attr("onclick", "saveUnitymol()")
}

var showTransparancySlider = function(hide_button){
    $("#transparency-div").attr("hidden", !hide_button)
}

var downloadFile = function(filename, data) {
    console.log(filename)
    console.log(data)

    // Create anchor element from which to download image
    let link = document.createElement('a');
    // let link = document.createElement('downloadFileAnchor');
    link.href = data;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

var downloadTextAsBlob = function(filename, data, content_type) {
    const blob = new Blob([data], {
        type: content_type
        // type: 'text/plain'
    });

    // Convert your blob into a Blob URL (a special url that points to an object in the browser's memory)
    const blobUrl = URL.createObjectURL(blob);

    // Create a link element
    const link = document.createElement("a");

    // Set link's href to point to the Blob URL
    link.href = blobUrl;
    link.download = filename;

    // Append link to the body
    document.body.appendChild(link);

    // Dispatch click event on the link
    // This is necessary as link.click() does not work on the latest firefox
    link.dispatchEvent(
        new MouseEvent('click', { 
            bubbles: true, 
            cancelable: true, 
            view: window 
        })
    );

    // Remove link from body
    document.body.removeChild(link);

}

// Create and download PyMol script
var savePymol = function() {
    let querystring_params = (new URL(document.location)).searchParams
    let job_id = querystring_params.get('jobid')
    let exported_filename = `${job_id}_PyMol.pml`

    // Set beginning text
    const heading_text = 
        '# The aboslute location of your files must be input below\n'
        + '# Rename lines 10, 11, and 27 to match your system\n'
        + '# Assuming you are on a windows machine and downloaded the files to your downloads folder, \n'
        + '# replace your username inplace of USERNAME to the path below\n\n'

        + '# Drag this script into an open PyMOL window\n'
        + '# The model will be loaded and also saved as a .pse file for ease of starting over\n\n'

        + '# Load the files\n'

    // Check OS to determine path style
    let template_dirpath_text = null
    if( navigator.platform.includes('Win') ){
        template_dirpath_text = 'C:\\<PATH_TO_DIRECTORY>\\'
    }else{
        template_dirpath_text = '/<PATH_TO_DIRECTORY>/'
    }

    // Set file/path names
    const structure_name = `${job_id}_APBS`
    const pqr_filepath = `${template_dirpath_text}${job_id}.pqr`
    const dx_filepath = `${template_dirpath_text}${job_id}-pot.dx`

    // Write remainder text
    const remaining_text = 
        `load ${pqr_filepath}, molecule\n`
        + `load ${dx_filepath}, electrostaticmap\n\n`

        + `# Set scale for coloring protein surface\n`
        + `ramp_new espramp, electrostaticmap, [ -3, 0, 3]\n\n`
        
        + `# Show the surface\n`
        + `show surface\n\n`
        
        + `# Set surface colors from dx\n`
        + `set surface_color, espramp\n`
        + `set surface_ramp_above_mode\n\n`
        
        + `# Setup export\n`
        + `set pse_export_version, 1.7\n\n`

        + `# Save file as .pse\n`
        + `save ${template_dirpath_text}${structure_name}.pse\n`


    // Combine and create full script text
    const all_data = heading_text + remaining_text

    // Download PyMol file
    downloadTextAsBlob(exported_filename, all_data, 'text/plain')

}

// Create and download UnityMol script
var saveUnitymol = function() {
    let querystring_params = (new URL(document.location)).searchParams
    let job_id = querystring_params.get('jobid')
    let exported_filename = `${job_id}_UnityMol.py`

    // Set beginning text
    const heading_text = 
        '# The aboslute location of your files must be input below\n'
        + '# Rename lines 9 and 10 to match your system\n'
        + '# Assuming you are on a windows machine and downloaded the files to your downloads folder, \n'
        + '# replace your username inplace of USERNAME to the path below\n\n'
        
        + '# Open this file in UnityMol using the "Load Script" button\n\n'

        + '# Load files\n'


    // Check OS to determine path style
    let template_dirpath_text = null
    if( navigator.platform.includes('Win') ){
        template_dirpath_text = 'C:/<PATH_TO_DIRECTORY>'
    }else{
        template_dirpath_text = '/<PATH_TO_DIRECTORY>'
    }

    // Set file/path names
    const structure_name = `${job_id}_APBS`
    const pqr_filepath = `${template_dirpath_text}/${job_id}.pqr`
    const dx_filepath = `${template_dirpath_text}/${job_id}-pot.dx`

    // Write remainder text
    const remaining_text = 
        `load(filePath="${pqr_filepath}", readHetm=True, forceDSSP=False, showDefaultRep=True, center=False);\n`
        + `loadDXmap("${structure_name}", "${dx_filepath}")\n\n`
        
        + `# Set selection and center\n`
        + `setCurrentSelection("all(${structure_name})")\n`
        + `centerOnSelection("all(${structure_name})", True)\n\n`
        
        + `# Show surface\n`
        + `showSelection("all(${structure_name})", "s")\n\n`

        + `# Color surface by charge\n`
        + `colorByCharge("all(${structure_name})", False, -10.000, 10.000)\n\n`

    // Combine and create full script text
    const all_data = heading_text + remaining_text

    // Download UnityMol file
    downloadTextAsBlob(exported_filename, all_data, 'text/plain')
}