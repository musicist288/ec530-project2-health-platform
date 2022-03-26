import { StatusBar } from 'expo-status-bar';
import {
    StyleSheet,
    Text,
    View,
    TextInput,
    Button,
    PickerItem
} from 'react-native';
import {
  Picker
} from '@react-native-picker/picker';
import { useState, useEffect } from 'react';

const base = "http://127.0.0.1:5000"

async function getRoles() {
  let response = await fetch(base + "/users/roles");
  let body = await response.json();
  return body.user_roles;
}

export default function LoginScreen({navigation}) {
  const [username, onUsernameChange] = useState("")
  const [password, onPasswordChange] = useState("")
  const [error, onError] = useState("")

  useEffect(() => {
    // Reset all the state on blur
    const unsubscribe = navigation.addListener('blur', () => {
      onUsernameChange("");
      onPasswordChange("");
      onError("");
    });
    return unsubscribe;
  }, [navigation]);

  const onLogin = async () => {
    let resp = null;
    try {
      resp = await fetch(base + `/users/login`, {
        method: "POST",
        body: JSON.stringify({
          username: username,
          password: password
        }),
        headers: {
          "Content-Type": "application/json; charset=UTF-8"
        }
      })
    } catch(err) {
      onError("There was an error connecting to the backend.")
    }

    if (resp == null) {
      return;
    }

    if (resp.status == 201) {
        let data = await resp.json()
        let user = data.user;
        navigation.navigate("User View", {user: user})
    }
    else {
        try {
            let data = await resp.json();
            onError(data.errors.join("<br />"));
        }
        catch (error) {
            onError("An unknown error occurred.")
        }
    }
  }

  return (
    <View style={styles.container}>
      <TextInput value={username}
                 placeholder="Username"
                 onChangeText={text => onUsernameChange(text)} style={styles.textInput} />

      <TextInput value={password}
                placeholder="Password"
                secureTextEntry={true}
                onChangeText={text => onPasswordChange(text)} style={styles.textInput} />
      <Text>{error}</Text>
      <View style={styles.buttonWrapper}>
        <Button
          title="Log In"
          onPress={() => onLogin()} />
      </View>
      <View style={styles.buttonWrapper}>
        <Button
          title="Register"
          onPress={() => navigation.navigate("Registration")} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  buttonWrapper: {
    marginBottom: 10
  },
  textInput: {
    height: 40,
    paddingHorizontal: 5,
    borderWidth: 1,
    borderColor: '#999',
    marginBottom: 10
  },
  labelText: {
    height: 40,
    fontSize: 20,
  },
  container: {
    flex: 1,
    paddingHorizontal: 20,
    paddingVertical: 10,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#000',
    alignItems: 'stretch',
    justifyContent: 'center',
  },
});
