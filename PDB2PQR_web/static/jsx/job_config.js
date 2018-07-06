'use strict';

class Button extends React.Component{

}
class SubmitButton extends React.Component{}
class FormWindowHeader extends React.Component{}

class FormWindow extends React.Component{
    render(){
        return(
            <MyButton color="blue" shadowSize={2}>
                Click Me
            </MyButton>
        )
    }    
}

class Configuration extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            jobtype: null,
            pdb2pqr_settings: null,
            apbs_settings: null,
        };
    }
    render(){
        if (this.state.jobtype === null){
            
        }
        else if (this.state.jobtype == "pdb2pqr"){}
        else if (this.state.jobtype == "apbs"){}
    }
}

ReactDOM.render(<Configuration />, document.getElementById('choose_job'))