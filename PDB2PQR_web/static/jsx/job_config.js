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
    createScrollspyToC(scrollspy_name, names_map){
        let all_headers = []
        names_map.forEach(function(value, key, map){
            all_headers.push(
                <a className="list-group-iterm list-group-item-action" href={'#'.concat(key)}>{value}</a>
            );
        })
        return(
            <div id={scrollspy_name} className="list-group">
                {all_headers}
            </div>
        )
    }

    // prepares the elements where user will enter information
    createConfigOptions(scrollspy_name){

        return(
            <div data-spy="scroll" data-target={'#'.concat(scrollspy_name)} className="list-group">

            </div>
        )
    }

    render(){

        return(
            <form>
                {this.createScrollspyToC(this.props.scrollspy_name, this.props.config_headers)}
                {this.createConfigOptions(this.props.scrollspy_name, this.props.config_headers)}
            </form>
        )
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
            document.body.id='body';
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
            let pdb2pqr_scrollspy = "pdb2pqr_config";
            let pdb2pqr_headers = new Map();
            pdb2pqr_headers.set("which_pdb",     "PDB ID Entry")
            pdb2pqr_headers.set("which_ff",      "Forcefield")
            pdb2pqr_headers.set("which_output",  "Output Naming Scheme")
            pdb2pqr_headers.set("which_options", "Output Naming Scheme")
            pdb2pqr_headers.set("which_pka",     "pKa Settings (optional)")
            pdb2pqr_headers.set("submission",    "Start Job")
            
            // document.body.data\-spy = 'body';
            $('#body').attr('data-spy', 'body')

            return(
                // <ConfigPDB2PQR
                //     scrollspy_name={pdb2pqr_scrollspy}
                //     config_headers={pdb2pqr_headers}
                // />
                <div className="row position-relative my-scrollspy-overflow-y">
                <div id="list-example" className="list-group col-2 position-fixed text-center">
                    <a class="list-group-item list-group-item-action active" href="#list-item-1">Item 1</a>
                    <a class="list-group-item list-group-item-action" href="#list-item-2">Item 2</a>
                    <a class="list-group-item list-group-item-action" href="#list-item-3">Item 3</a>
                    <a class="list-group-item list-group-item-action" href="#list-item-4">Item 4</a>
                </div>
                <div data-spy="scroll" data-target="#list-example" data-offset="0" className="col-8 ">
                    <h4 id="list-item-1">Item 1</h4>
                    <p>Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore.
Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore.
Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore.
Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore.
</p>
                    <h4 id="list-item-2">Item 2</h4>
                    <p>Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore.
Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore.
Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore.
Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore.
</p>
                    <h4 id="list-item-3">Item 3</h4>
                    <p>Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore.
Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore.
Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore.
Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore.
</p>
                    <h4 id="list-item-4">Item 4</h4>
                    <p>Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore.
Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore.
Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore.
Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore.
</p>
                </div>                
                </div>                
            )
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