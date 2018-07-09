'use strict';

// class SubmitButton extends React.Component{}
// class FormWindowHeader extends React.Component{}

class SelectJob extends React.Component{
    render(){
        return(
            <div className="btn-group">
                <button type="button" className="btn btn-primary">PDB2PQR</button>
                <button type="button" className="btn btn-primary">APBS</button>
            </div>
        )
    };
}

function Button(props){
    return(
        <button type="button" className={props.buttonType} onClick={props.onClick}>
            {props.value}
        </button>
    )
}

class FormWindow extends React.Component{
    createButton(txt){
        return(
            <Button
                value={txt}
                buttonType="btn btn-primary"
                onClick={() => this.props.onClick(txt)}
            />
        )
    }

    createWindow(option_list){
        let view = [];

        for(let i = 0; i < option_list.length; i++){
            view.push(this.createButton(option_list[i]));
        }

        return view;
    }

    render(){
        // let choices = [];
        // this.props.job_list.forEach(function(element){
            // choices.push(this.renderButton(element))
        // });
        // console.log(choices)
        // numJobs = this.props.job_list.length;

        return(
            <div className="container">
                <div className="row">
                    <div className="col-lg-12">
                        <div className="btn-group">
                            {/* {this.createButton(this.props.job_list[0])} */}
                            {/* {this.createButton("PDB2PQR")} */}
                            {/* {this.createButton("APBS")} */}
                            {this.createWindow(this.props.job_list)}
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}

class Configuration extends React.Component{
    constructor(props){
        super(props);
        this.selectJobClick = this.selectJobClick.bind(this)
        this.state = {
            job_type: null,
            pdb2pqr_settings: {
                pdb_id: null,
                ff: null,
                output_scheme: null,
            },
            apbs_settings: {},
        };
    }

    selectJobClick(selected_job){
        this.setState({
            job_type: selected_job
        })
        console.log(this.state.job_type)
    }

    render(){
        if (this.state.job_type == null){
            let job_options = ["PDB2PQR", "APBS"]
            // let blah = <FormWindow onClick={j => this.selectJobClick(j)}/>
            return(
                <FormWindow 
                    job_list={job_options}
                    onClick={j => this.selectJobClick(j)}
                />
            );
        }
        else if (this.state.job_type == "PDB2PQR"){
            return("Selected PDB2PQR")
        }
        else if (this.state.job_type == "APBS"){
            console.log("selected apbs")
            return("Selected APBS")
        }
        else{
            return ("job_type is invalid")
        }
    }
}

// let domContainer = );
ReactDOM.render(<Configuration />, document.getElementById('choose_job'));