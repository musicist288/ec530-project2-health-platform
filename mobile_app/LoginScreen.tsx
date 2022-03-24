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

  const onLogin = async () => {
    let resp = await fetch(base + `/users?email=${username}`)

    if (resp.status == 200) {
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
      <Button
        title="Log In"
        onPress={() => onLogin()} />
      <Button
        title="Register"
        onPress={() => navigation.navigate("Registration")} />
    </View>
  );
}

const styles = StyleSheet.create({
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
