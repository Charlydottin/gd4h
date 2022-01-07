import {
    Col, Toggle,
  } from '@dataesr/react-dsfr';
  
class Toggle extends React.Component {
  constructor(props) {
    super(props);
    this.state = {isToggleOn: true};

    // This binding is necessary to make `this` work in the callback    
    this.handleClick = this.handleClick.bind(this);  }

  handleClick(){    
      this.setState(prevState => ({      isToggleOn: !prevState.isToggleOn    }));  
    }
  render() {
    return (
        
        <div class="fr-toggle fr-toggle--label-left">
        <input
          type="checkbox"
          class="fr-toggle__input" 
          aria-describedby="toggle-726-hint-text" id="toggle-726"
          value={this.state.isToggleOn ? 'FR' : 'EN'}
          onClick={this.handleClick}
        />            
            <label class="fr-toggle__label" for="toggle-726" data-fr-checked-label="FR" data-fr-unchecked-label="EN">Changer de langue</label>
            
        </div>
      
    );
  }
  }
  const ToggleExample = () => (
    <>
      <Col>
        <Toggle
          onChange={() => { }}
          disabled
          checked
          label="Toggle Label"
          description="Toggle descirption"
        />
      </Col>
    </>
      )
  export default ToggleExample;