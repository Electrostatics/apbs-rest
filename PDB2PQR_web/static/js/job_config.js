'use strict';

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Button = function (_React$Component) {
    _inherits(Button, _React$Component);

    function Button() {
        _classCallCheck(this, Button);

        return _possibleConstructorReturn(this, (Button.__proto__ || Object.getPrototypeOf(Button)).apply(this, arguments));
    }

    return Button;
}(React.Component);

var SubmitButton = function (_React$Component2) {
    _inherits(SubmitButton, _React$Component2);

    function SubmitButton() {
        _classCallCheck(this, SubmitButton);

        return _possibleConstructorReturn(this, (SubmitButton.__proto__ || Object.getPrototypeOf(SubmitButton)).apply(this, arguments));
    }

    return SubmitButton;
}(React.Component);

var FormWindowHeader = function (_React$Component3) {
    _inherits(FormWindowHeader, _React$Component3);

    function FormWindowHeader() {
        _classCallCheck(this, FormWindowHeader);

        return _possibleConstructorReturn(this, (FormWindowHeader.__proto__ || Object.getPrototypeOf(FormWindowHeader)).apply(this, arguments));
    }

    return FormWindowHeader;
}(React.Component);

var FormWindow = function (_React$Component4) {
    _inherits(FormWindow, _React$Component4);

    function FormWindow() {
        _classCallCheck(this, FormWindow);

        return _possibleConstructorReturn(this, (FormWindow.__proto__ || Object.getPrototypeOf(FormWindow)).apply(this, arguments));
    }

    _createClass(FormWindow, [{
        key: "render",
        value: function render() {
            return React.createElement(
                MyButton,
                { color: "blue", shadowSize: 2 },
                "Click Me"
            );
        }
    }]);

    return FormWindow;
}(React.Component);

var Configuration = function (_React$Component5) {
    _inherits(Configuration, _React$Component5);

    function Configuration(props) {
        _classCallCheck(this, Configuration);

        var _this5 = _possibleConstructorReturn(this, (Configuration.__proto__ || Object.getPrototypeOf(Configuration)).call(this, props));

        _this5.state = {
            jobtype: null,
            pdb2pqr_settings: null,
            apbs_settings: null
        };
        return _this5;
    }

    _createClass(Configuration, [{
        key: "render",
        value: function render() {
            if (this.state.jobtype === null) {} else if (this.state.jobtype == "pdb2pqr") {} else if (this.state.jobtype == "apbs") {}
        }
    }]);

    return Configuration;
}(React.Component);

ReactDOM.render(React.createElement(Configuration, null), document.getElementById('choose_job'));