import {
    StyleSheet,
    Text,
    View,
    TextInput,
    Button,
    ScrollView
} from 'react-native';

import { useState, useEffect } from 'react';
import { BaseURL } from './config';
import { Logout } from "./LoginScreen";

async function getRoles() {
    let response = await fetch(BaseURL + "/users/roles");
    let body = await response.json();
    return body.user_roles;
}

async function getUser(username: String) {
    let resp = await fetch(BaseURL + `/users?email=${username}`);
    if (resp.status == 200) {
        let data = await resp.json();
        return data['user'];
    }
    else {
        return null;
    }
}

export default function UserView({route, navigation}) {
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
        <ScrollView contentContainerStyle={styles.container}>
            <Text>Name: {user.first_name} {user.last_name}</Text>
            <Text>DOB: {user.dob}</Text>

            <Text>Medical Staff</Text>
            {staffRendering}

            <Button title="Log Out" onPress={() => {
                Logout().then(() => navigation.navigate("Login"));
            }} />
        </ScrollView>
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
