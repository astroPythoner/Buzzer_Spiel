class ButtonPin
{
  private:
    const int button_in;
    const int button_out;
    const int led_1;
    const int led_2;

  public:
    ButtonPin(const int button_in,const int button_out,const int led_1,const int led_2): button_in(button_in), button_out(button_out), led_1(led_1), led_2(led_2)
    {
      // init leds
      pinMode(led_1, OUTPUT);
      pinMode(led_2, OUTPUT);
      // init button
      pinMode(button_out, OUTPUT);
      digitalWrite(button_out, LOW);
      pinMode(button_in, INPUT_PULLUP);
    }

    bool check() {
      // check button of pressed return true else turn on led and return false
      if (digitalRead(button_in) == LOW) {
        return true;
      }
      else {
        on();
        return false;
      }
    };

    void off() {
      digitalWrite(led_1, LOW);
      digitalWrite(led_2, LOW);
    };
    void on() {
      digitalWrite(led_1, HIGH);
      digitalWrite(led_2, LOW);
    };
    void on_2() {
      digitalWrite(led_1, LOW);
      digitalWrite(led_2, HIGH);
    };
};

// buttons and pins ButtonPin(button_in,button_out,led1,led2)
const int num_buttons = 8;
ButtonPin all_pins[num_buttons] = {ButtonPin(47,53,49,51),ButtonPin(52,46,50,48),ButtonPin(39,45,41,43),ButtonPin(44,38,42,40),ButtonPin(31,37,33,35),ButtonPin(36,30,34,32),ButtonPin(23,29,25,27),ButtonPin(28,22,26,24)};
int found = -1;
long time_since_press = 0;

bool manual_mode = false; // in manual mode the arduino doesnt listen the port but is controlled with a button
const int BUTTON_PIN = 10; // Button to controll in manual mode
bool last_read = false;

// modes and input
enum mode {
  show_init,
  checking,
  nothing
};
int selected_pins[num_buttons]; // stores which pins are enabled
char teams[num_buttons]; // stores in which team the buttons are
mode current_mode = nothing;
String input;

void setup() {
  Serial.begin(9600);
  Serial.println("Welcome");
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  for (size_t i = 0; i < num_buttons; i++) {
    selected_pins[i] = true;
    teams[i] = i;
  }
  if (digitalRead(BUTTON_PIN) == LOW) {
    manual_mode = true;
  }
}

void loop() {
  // waiting for button press
  if (current_mode == checking) {
    if (found == -1) {
      // if no button is found yet loop through buttons to check them
      for (size_t i = 0; i < num_buttons; i++) {
        if (selected_pins[i] == true) {
          if(all_pins[i].check() == true){
            // if check retuns true (button is pressed) save which button it was
            found = i;
            time_since_press = millis();
          }
        }
        else {
          all_pins[i].off();
        }
      }
    }
    else {
      // if a button is already found loop through buttons and turn them off or blink the pressed one
      for (size_t i = 0; i < num_buttons; i++) {
        if (selected_pins[i] == true) {
          if(found == i) {
            // blink with the pressed one
            if ((millis()-time_since_press)%120 < 50) { all_pins[i].on(); }
            else { all_pins[i].on_2(); }
          }
          else if(teams[found] == teams[i]) {
            all_pins[i].on_2();
          }
          else {
            // turn the others off
            all_pins[i].off(); 
          }
        }
        else {
          all_pins[i].off();
        }
      }
    }
  }
  // showing enabled buttons
  else if(current_mode == show_init) {
    for (size_t i = 0; i < num_buttons; i++) {
      if (selected_pins[i] == true) {
        all_pins[i].on_2();
      }
      else {
        all_pins[i].off();
      }
    }
  }
  // all leds off
  else if(current_mode == nothing) {
    for (size_t i = 0; i < num_buttons; i++) {
      all_pins[i].off();
    }
  }

  // manuel mode change via button
  if (manual_mode == true) {
    if (digitalRead(BUTTON_PIN) == LOW) {
      if (last_read == false) {
        if (current_mode == nothing) {
          found = -1;
          current_mode = checking;
        }
        else {
          current_mode = nothing;
        }
      }
      last_read = true;
    }
    else {
      last_read = false;
    }
  }
  // settings via serial port
  else {
    // read serial input
    if (Serial.available()) {
      //Serial.println("read");
      input = Serial.readStringUntil('\n');
      //Serial.println("got:"+input);
      if (input == "s") {
        current_mode = checking;
        found = -1;
        Serial.println("-");
      }
      else if (input == "i") {
        current_mode = show_init;
        Serial.println("-");
      }
      else if (input == "o") {
       current_mode = nothing;
       Serial.println("-");
      }
      else if (input == "g") {
        Serial.println(found+1);
      }
      else if (input == "r") {
        found = -1;
        current_mode = nothing;
        for (size_t i = 0; i < num_buttons; i++) {
          teams[i] = i;
        }
        for (size_t i = 0; i < num_buttons; i++) {
          selected_pins[i] = true;
        }
        Serial.println("-");
      }
      else if (input[0] == 'c') {
        if (input.length() <= num_buttons) {
          Serial.println("e");
        }
        else {
          for (size_t i = 1; i <= num_buttons; i++) {
            if (input[i] == '1') {selected_pins[i-1] = true;}
            else {selected_pins[i-1] = false;}
          }
          Serial.println("-");
        }
      }
      else if (input[0] == 't') {
        if (input.length() <= num_buttons) {
          Serial.println("e");
        }
        else {
          for (size_t i = 1; i <= num_buttons; i++) {
            teams[i-1] = input[i];
          }
          Serial.println("-");
        }
      }
      else if (input == "h") {
        Serial.println("Help:   "\
        "s: Start wating for button presses - " \
        "g: Get pressed button - " \
        "i: Init (light up left led of all enabled buttons) - " \
        "o: Off (all Leds off, if in waiting mode or init mode leave it) - " \
        "c<enabled>: Configure Buttons (e.x. c10111111 would enable all buttons but second) - " \
        "t<enabled>: Configure Temas (e.x. c01102120 all 0s, 1s and 2s will be in a team) - " \
        "r: Reset (all Leds off, all buttons enabled, no teams) - " \
        "returns: a minus is returned when command was successfull, e is returned if there was an Error"
        );
      }
      else {
        Serial.println("e");
      }
    }
  }
}
