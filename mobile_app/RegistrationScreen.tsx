import { StatusBar } from 'expo-status-bar';
import {
    StyleSheet,
    Text,
    View,
    TextInput,
    Button,
    ScrollView,
} from 'react-native';

import {
    Picker
} from '@react-native-picker/picker';

import DatePicker from "react-native-date-picker";

import { useState, useEffect } from 'react';

import { BaseURL } from './config';

async function getRoles() {
    let response = await fetch(BaseURL + "/users/roles");
    let body = await response.json();
    return body.user_roles;
}

export default function RegistrationScreen({navigation}) {
    const defaultDOB = new Date("2010-01-01");
    const [username, onUsernameChange] = useState("")
    const [firstName, onFirstName] = useState("")
    const [lastName, onLastName] = useState("")
    const [role, onRoleChange] = useState("")
    const [password, onPasswordChange] = useState("");
    const [dob, onDOBChange] = useState(defaultDOB)
    const [error, onError] = useState("")

    useEffect(() => {
        // Reset all the state on blur
        const unsubscribe = navigation.addListener('blur', () => {
            onUsernameChange("");
            onPasswordChange("");
            onFirstName("");
            onLastName("");
            onDOBChange(defaultDOB);
            onError("");
        });
        return unsubscribe;
    }, [navigation]);

    const [availableRoles, onAvailableRoleChange] = useState([])

    const onRegister = async () => {
        let resp = null;
        try {
            resp = await fetch(BaseURL + "/users", {
                method: "POST",
                body: JSON.stringify({
                    first_name: firstName,
                    last_name: lastName,
                    dob: dob,
                    email: username,
                    password: password,
                    role_ids: [role]
                }),
                headers: {
                    "Content-Type": "application/json; charset=UTF-8"
                }
            })
        }
        catch(err) {
            onError("There was an error connecting to the backend.");
            console.error(err);
            return;
        }

        if (resp.status == 200) {
            let data = await resp.json()
            navigation.navigate("Login")
        }
        else {
            try {
                let json = await resp.json();
                onError((json.errors || []).join("\n"))
            }
            catch (err) {
                let data = await resp.text();
                console.error("Non-json response", data);
            }
        }
    }

    useEffect(() => {
        getRoles().then((user_roles) => {
            let roles = user_roles.filter((u) => u.role_name != "Admin")
            onAvailableRoleChange(roles); // Set the picker list items
            let patientOnly = roles.filter((u) => u.role_name == "Patient");
            if (patientOnly.length) {
                roles =  patientOnly;
            }
            onRoleChange(roles[0].role_id); // Set the default role
        });
    }, []);
    const [open, setOpen] = useState(false)
    return (
        <ScrollView>
            <TextInput value={username}
                placeholder="Username"
                onChangeText={text => onUsernameChange(text)} style={styles.textInput} />

            <TextInput
                value={firstName}
                placeholder="First Name"
                onChangeText={text => onFirstName(text)} style={styles.textInput} />

            <TextInput value={lastName}
                placeholder="Last Name"
                onChangeText={text => onLastName(text)}
                style={styles.textInput} />

            <Button title={"DOB: " + dob.toLocaleDateString()} onPress={() => setOpen(true)} />

            <DatePicker
                modal
                open={open}
                date={dob}
                mode="date"
                onConfirm={(date) => {
                    setOpen(false)
                    onDOBChange(date)
                }}
                onCancel={() => {
                    setOpen(false)
                }}
                />

            <Picker selectedValue={role}
                style={styles.textInput}
                onValueChange={(value, index) => onRoleChange(value)}>
                {
                    availableRoles.map((role) => {
                        return <Picker.Item label={role.role_name} value={role.role_id} key={role.role_id}></Picker.Item>
                    })
                }
            </Picker>

            <TextInput value={password}
                placeholder="Password"
                secureTextEntry={true}
                onChangeText={text => onPasswordChange(text)} style={styles.textInput} />
            <View style={styles.buttonWrapper}>
                <Text style={styles.errorText}>{error}</Text>
            </View>
            <View style={styles.buttonWrapper}>
                <Button title="Register"
                        onPress={() => onRegister()} />
            </View>
            <View style={styles.buttonWrapper}>
                <Button title="Log In"
                        onPress={() => navigation.navigate("Login")} />
            </View>
        </ScrollView>
        );
    }

    const styles = StyleSheet.create({
        errorText: {
            color: "#f35353"
        },
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
