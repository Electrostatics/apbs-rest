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
    renderButton(txt){
        return(
            <Button
                value={txt}
                buttonType="btn btn-primary"
                onClick={() => this.props.onClick(txt)}
            />
        )
    }

    render(){
        return(
            <div className="btn-group">
                {this.renderButton("PDB2PQR")}
                {this.renderButton("APBS")}
                {this.renderButton("APBSSKLADFH")}
            </div>
        )
    }
}

class Configuration extends React.Component{
    constructor(props){
        super(props);
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

    selectJobClick(jobtype){
        this.setState({
            job_type: jobtype
        })
        console.log(this.state.job_type)
    }

    render(){
        if (this.state.jobtype == null){
            let blah = <FormWindow onClick={j => this.selectJobClick(j)}/>
            return(
                blah
            );
        }
        else if (this.state.jobtype == "pdb2pqr"){}
        else if (this.state.jobtype == "apbs"){console.log("selected apbs")}
    }
}

// let domContainer = );
ReactDOM.render(<Configuration />, document.getElementById('choose_job'));