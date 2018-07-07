'use strict';

// class SubmitButton extends React.Component{}
// class FormWindowHeader extends React.Component{}

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var SelectJob = function (_React$Component) {
    _inherits(SelectJob, _React$Component);

    function SelectJob() {
        _classCallCheck(this, SelectJob);

        return _possibleConstructorReturn(this, (SelectJob.__proto__ || Object.getPrototypeOf(SelectJob)).apply(this, arguments));
    }

    _createClass(SelectJob, [{
        key: "render",
        value: function render() {
            return React.createElement(
                "div",
                { className: "btn-group" },
                React.createElement(
                    "button",
                    { type: "button", className: "btn btn-primary" },
                    "PDB2PQR"
                ),
                React.createElement(
                    "button",
                    { type: "button", className: "btn btn-primary" },
                    "APBS"
                )
            );
        }
    }]);

    return SelectJob;
}(React.Component);

function Button(props) {
    return React.createElement(
        "button",
        { type: "button", className: props.buttonType, onClick: props.onClick },
        props.value
    );
}

var FormWindow = function (_React$Component2) {
    _inherits(FormWindow, _React$Component2);

    function FormWindow() {
        _classCallCheck(this, FormWindow);

        return _possibleConstructorReturn(this, (FormWindow.__proto__ || Object.getPrototypeOf(FormWindow)).apply(this, arguments));
    }

    _createClass(FormWindow, [{
        key: "renderButton",
        value: function renderButton(txt) {
            var _this3 = this;

            return React.createElement(Button, {
                value: txt,
                buttonType: "btn btn-primary",
                onClick: function onClick() {
                    return _this3.props.onClick(txt);
                }
            });
        }
    }, {
        key: "render",
        value: function render() {
            return React.createElement(
                "div",
                { className: "btn-group" },
                this.renderButton("PDB2PQR"),
                this.renderButton("APBS"),
                this.renderButton("APBSSKLADFH")
            );
        }
    }]);

    return FormWindow;
}(React.Component);

var Configuration = function (_React$Component3) {
    _inherits(Configuration, _React$Component3);

    function Configuration(props) {
        _classCallCheck(this, Configuration);

        var _this4 = _possibleConstructorReturn(this, (Configuration.__proto__ || Object.getPrototypeOf(Configuration)).call(this, props));

        _this4.state = {
            job_type: null,
            pdb2pqr_settings: {
                pdb_id: null,
                ff: null,
                output_scheme: null
            },
            apbs_settings: {}
        };
        return _this4;
    }

    _createClass(Configuration, [{
        key: "selectJobClick",
        value: function selectJobClick(jobtype) {
            this.setState({
                job_type: jobtype
            });
            console.log(this.state.job_type);
        }
    }, {
        key: "render",
        value: function render() {
            var _this5 = this;

            if (this.state.jobtype == null) {
                var blah = React.createElement(FormWindow, { onClick: function onClick(j) {
                        return _this5.selectJobClick(j);
                    } });
                return blah;
            } else if (this.state.jobtype == "pdb2pqr") {} else if (this.state.jobtype == "apbs") {
                console.log("selected apbs");
            }
        }
    }]);

    return Configuration;
}(React.Component);

// let domContainer = );


ReactDOM.render(React.createElement(Configuration, null), document.getElementById('choose_job'));