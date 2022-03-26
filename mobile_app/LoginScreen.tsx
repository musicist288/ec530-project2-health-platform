import { StatusBar } from 'expo-status-bar';
import {
    StyleSheet,
    Text,
    View,
    TextInput,
    Button
} from 'react-native';

import { useState, useEffect } from 'react';
import { BaseURL } from './config';
import AsyncStorage from '@react-native-async-storage/async-storage';

async function onLogin(username: String, password: String) {
    let resp = null;
    let url = BaseURL + `/users/login`;
    console.log(url);
    try {
        resp = await fetch(url, {
            method: "POST",
            body: JSON.stringify({
                username: username,
                password: password
            }),
            headers: {
                "Content-Type": "application/json; charset=UTF-8"
            }
        })
    }
    catch(err) {
        console.error(err);
        throw new Error("There was an error connecting to the backend.");
    }

    if (resp == null) {
        return;
    }

    if (resp.status == 201) {
        let data = await resp.json()
        let user = data.user;
        return user;
    }
    else {
        console.log("Bad response", resp.status);
        let errors;
        try {
            let data = await resp.json();
            errors = data.errors;
        }
        catch (error) {
            console.error(error)
            throw new Error("An unknown error occurred.")
        }

        if (errors) {
            throw new Error(errors.join("\n"));
        }
    }
}

async function Logout() {
    await AsyncStorage.removeItem("currentUser");
}

async function getLoggedInUser() {
    try {
        let item = await AsyncStorage.getItem("currentUser");
        if (item) {
            try  {
                let user = JSON.parse(item);
                return user;
            }
            catch(err) {
                console.error("Could not deserialize current user.");
            }
        }
        else {
            console.info("No logged in user.")
        }
    }
    catch (err) {
        console.error("Error getting item:", err);
    }
}



export { Logout };

export default function LoginScreen({navigation}) {
    const [username, onUsernameChange] = useState("");
    const [password, onPasswordChange] = useState("");
    const [error, onError] = useState("");

    useEffect(() => {
        // Reset all the state on blur
        const unsubscribe = navigation.addListener('blur', () => {
            onUsernameChange("");
            onPasswordChange("");
            onError("");
        });

        getLoggedInUser().then(function (user) {
            if (user != undefined) {
                console.log("Logged in user: ", user);
                navigation.navigate("User View", {user});
            }
            else {
                console.log("No user logged in")
            }
        });

        return unsubscribe;
    }, [navigation]);


    const doLogin = function() {
        onLogin(username, password).then(function (user) {
            console.log("Login Finished")
            if (user != undefined) {
                AsyncStorage.setItem("currentUser", JSON.stringify(user));
                navigation.navigate("User View", {user});
            }
            else {
                onError("Login Failed");
            }
        }).catch(function (err) {
            console.log("Login Error", err)
            onError(err.message);
        });
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
            <Button title="Log In"
                    onPress={() => doLogin()} />
            </View>
            <View style={styles.buttonWrapper}>
            <Button title="Register"
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
