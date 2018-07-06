'use strict';

class Button extends React.Component{}
class SubmitButton extends React.Component{}

class ButtonWindow extends React.Component{
    constructor(props){

    }
}

class Configuration extends React.Component{
    constructor(props){
        this.state = { jobtype: null }
    }
    render(){
        if (this.state.jobtype === null){

        }
    }
}

ReactDOM.render(<Configuration />, document.getElementById('choose_job'))