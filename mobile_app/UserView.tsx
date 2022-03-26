import {
    StyleSheet,
    Text,
    View,
    TextInput,
    Button,
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

async function getUser(username: String) {
    let resp = await fetch(base + `/users?email=${username}`);
    if (resp.status == 200) {
        let data = await resp.json();
        return data['user'];
    }
    else {
        return null;
    }
}

export default function LoginScreen({route, navigation}) {
    let user = route.params.user;
    useEffect(() => {
        getUser(user.email).then(function (user) {
            console.log(user);
        })
    }, []);

    let staffRendering = null;
    if (user.medical_staff.length) {
        staffRendering = <Text>toDO inplemente</Text>
    }
    else {
        staffRendering = <Text>There are no medical staff assigned to this patient.</Text>
    }

    return (
        <View style={styles.container}>
            <Text>Name: {user.first_name} {user.last_name}</Text>
            <Text>DOB: {user.dob}</Text>
            <Text>Medical Staff</Text>
            {staffRendering}
            <Button title="Log Out" onPress={() => navigation.navigate("Login")} />
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
