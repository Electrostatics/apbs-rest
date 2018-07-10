'use strict';

// class SubmitButton extends React.Component{}
// class FormWindowHeader extends React.Component{}

function Button(props){
    return(
        <button type="button" className={props.buttonType} onClick={props.onClick}>
            {props.value}
        </button>
    )
}

class JobLanding extends React.Component{
    createButton(txt, additional_classNames){
        return(
            <Button
                value={txt}
                buttonType={additional_classNames}
                onClick={() => this.props.onClick(txt)}
            />
        )
    }

    createWindow(option_list){
        let view = [];

        for(let i = 0; i < option_list.length; i++){
            view.push(this.createButton(option_list[i], "btn btn-primary mx-1"));
        }

        return view;
    }

    render(){
        return(
            <section className="jumbotron text-center">
                <div className="container">
                    <h1 className="jumbotron-heading">
                        Welcome to the PDB2PQR Server
                    </h1>
                    <p className="lead text-muted">
                        This server enables a user to convert PDB files into PQR files.
                        PQR files are PDB files where the occupancy and B-factor columns
                        have been replaced by per-atom charge and radius.
                    </p>
                    <p>
                        {this.createWindow(this.props.job_list)}
                    </p>
                </div>
            </section>
        )
    }
}

class ConfigPDB2PQR extends React.Component{
    // prepares the list-group for the parts of configuration
    createScrollspyToC(){
        
    }

    // prepares the elements where user will enter information
    createConfigOptions(){

    }
}

class Configuration extends React.Component{
    constructor(props){
        super(props);
        this.selectJobClick = this.selectJobClick.bind(this)
        this.state = {
            job_type: null,

            // Maintains state for PDB2PQR configuration in case user hops back and forth
            pdb2pqr_settings: {
                pdb_id: null,
                ff: null,
                output_scheme: null,
            },
            
            // Maintains state for APBS for same purpose as pdb2pqr_settings
            apbs_settings: {

            },
        };
    }

    // onClick handler for user selecting a job. Is passed into child componenets
    selectJobClick(selected_job){
        this.setState({
            job_type: selected_job
        })
    }

    // 
    handleConfigClick(selected_job, option, selection){
        this.setState({
            selected_job: {
                option: selection
            }
        })
    }

    render(){
        // Renders landing page, with choice to do PDB2PQR or APBS
        if (this.state.job_type == null){
            let job_options = ["PDB2PQR", "APBS"]
            // let blah = <JobLanding onClick={j => this.selectJobClick(j)}/>
            return(
                <JobLanding 
                    job_list={job_options}
                    onClick={j => this.selectJobClick(j)}
                />
            );
        }

        // Renders configuration elements to set up an PDB2PQR job
        else if (this.state.job_type == "PDB2PQR"){
            return("Selected PDB2PQR")
        }

        // Renders configuration elements to set up an APBS job
        else if (this.state.job_type == "APBS"){
            return("Selected APBS")
        }

        // This should be unreachable since the state is only changed via a button press
        else{
            return ("job_type is invalid")
        }
    }
}

// let domContainer = );
ReactDOM.render(<Configuration />, document.getElementById('choose_job'));