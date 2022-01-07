import React from 'react';

class Toggle extends React.Component {
constructor(props) {
  super(props);
  this.state = {isToggleOn: true};

  // This binding is necessary to make `this` work in the callback    
  this.handleClick = this.handleClick.bind(this);  }

handleClick(){    
  console.log(this.state);  
  this.setState(prevState => ({      isToggleOn: !prevState.isToggleOn    }));  
  }
render() {
  return (
    <div class="fr-form-group sm">
    <fieldset class="fr-fieldset">
        <legend class="fr-fieldset__legend fr-text--regular" id='radio-legend'>
            Changer de langue:
        </legend>
        <div class="fr-fieldset__content">
            <div class="fr-radio-group">
                <input type="radio" id="radio-1" name="radio" checked />
                <label class="fr-label" for="radio-1">Français
                </label>
            </div>
            <div class="fr-radio-group">
                <input type="radio" id="radio-2" name="radio" />
                <label class="fr-label" for="radio-2">Anglais
                </label>
            </div>
            
        </div>
    </fieldset>
    </div>
    
  );
};
}

const ChangeLang = () => (
  <>
      
      <Toggle/>
      
  </>
    )
export default ChangeLang;
