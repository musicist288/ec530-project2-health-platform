import {
    StyleSheet,
    Text,
    View,
    Pressable,
    ScrollView,
    FlatList,
    TouchableOpacity
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

async function getStaffList() {
    let resp = await fetch(BaseURL + "/users?role=Doctor");
    if (resp.status == 200) {
        let data = await resp.json();
        return data.users;
    }
}

async function getPatientList() {
    let resp = await fetch(BaseURL + "/users?role=Patient");
    if (resp.status == 200) {
        let data = await resp.json();
        return data.users;
    }
}

async function updateUser(user) {
    user.medical_staff_ids = user.medical_staff.map((m) => m.user_id)
    user.patient_ids = user.patients.map((m) => m.user_id)
    user.role_ids = user.roles.map((m) => m.role_id)
    console.log("Updating user", user);

    try {
        let resp = await fetch(BaseURL + "/users/" + user.user_id.toString(), {
            method: "POST",
            body: JSON.stringify(user),
            headers: {"Content-Type": "application/json"}
        });

        console.log("Got response", resp);
        if (resp.status == 200) {
            return;
        }
        else {
            let data = await resp.json();
            console.log("Error updatin guser", resp.status, data);
        }
    }
    catch(err) {
        console.error("Error updating user: ", err);
    }
}

export default function UserView({route, navigation}) {
    let user = route.params.user;
    let [mode, onMode] = useState("overview");
    let [userList, onUserList] = useState([]);
    let [userSelection, onUserSelection] = useState([]);

    useEffect(() => {
        getUser(user.email).then(function (user) {
            if (!user) {
                Logout();
            }
        })
    }, []);

    let patientsRendering = null;
    if (user.patients.length) {
        patientsRendering = (
            <View>
                {user.patients.map((u) => {
                    return (
                        <View style={styles.relationship}>
                            <Text key={u.user_id} style={styles.relName}>{u.first_name} {u.last_name}</Text>
                            <Text style={styles.relDOB}>DOB: {user.dob}</Text>
                        </View>
                    )
                })}
            </View>
        );
    }
    else {
        patientsRendering = <Text>There are no patients to this doctor.</Text>
    }

    function addMedicalStaff() {
        getStaffList().then(function (staff) {
            onUserList(staff);
            let selected = user.medical_staff.map((s) => s.user_id)
            console.log(selected)
            onUserSelection(selected);
            onMode("addStaff");
        });
    }

    function addPatients() {
        getPatientList().then(function (users) {
            onUserList(users);
            onMode("addPatients");
        });
    }

    function assign() {
        if (mode == "addPatients") {
            user.patients = userList.filter((u) => userSelection.includes(u.user_id));
        }
        else {
            user.medical_staff = userList.filter((u) => userSelection.includes(u.user_id));
        }

        updateUser(user).then(() => onMode("overview"));
    }

    const Item = ({ item, onPress, backgroundColor, textColor }) => (
        <TouchableOpacity onPress={onPress} style={[styles.item, backgroundColor]}>
            <Text style={[styles.title, styles.itemLabel, textColor]}>{item.title}</Text>
        </TouchableOpacity>
    );

    function updateSelection(item) {
        let newSelection = userSelection;
        if (userSelection.includes(item.id)) {
            newSelection = userSelection.filter((i) => i != item.id);
        }
        else {
            newSelection = userSelection.concat([item.id]);
        }
        onUserSelection(newSelection);
    }

    const renderItem = ({ item }) => {
        const backgroundColor = userSelection.includes(item.id) ? "#6e3b6e" : "#ffffff";
        const color = userSelection.includes(item.id) ? 'white' : 'black';

        return (
            <Item
                item={item}
                onPress={() => updateSelection(item)}
                backgroundColor={{ backgroundColor }}
                textColor={{ color }}
            />
        );
    };

    return (
        <View style={styles.wrapper}>
                { mode == "overview" ? (
                    <ScrollView contentContainerStyle={styles.container}>
                    <View>
                        <Text>Name: {user.first_name} {user.last_name}</Text>
                        <Text>Patients</Text>
                        {patientsRendering}
                        <Pressable style={styles.addRelationship} onPress={addPatients}>
                            <Text style={styles.buttonLabel}>Add Patients</Text>
                        </Pressable>
                    </View>
                    </ScrollView>
                ) :   (
                    <FlatList
                        renderItem={renderItem}
                        keyExtractor={(item) => item.id}
                        extraData={userSelection}
                        data={userList.map((u) => {
                            return {
                                id: u.user_id,
                                title:
                                `${u.first_name} ${u.last_name}`
                            };
                        })} />
                )}
            <View style={styles.bottomBar}>
                { mode == "overview" ? (
                    <Pressable style={styles.button} onPress={() => {
                        Logout().then(() => navigation.navigate("Login"));
                    }}>
                        <Text style={styles.buttonLabel}>Log Out</Text>
                    </Pressable>
                ) : (
                    <Pressable style={styles.button} onPress={assign}>
                        <Text style={styles.buttonLabel}>Assign</Text>
                    </Pressable>
                )}
            </View>
        </View>
        );
    }

    const styles = StyleSheet.create({
        addRelationship: {
            marginTop: 5,
            height: 44,
            borderRadius: 6,
            backgroundColor: "#008AE8",
            justifyContent: "center"
        },
        item: {
            height: 40,
            alignItems: 'stretch',
            justifyContent: "center",
            borderWidth: 1,
            borderColor: "#999"
        },
        itemLabel: {
            paddingLeft: 20,
        },
        button: {
            flex: 1,
            backgroundColor: "#008AE8",
            alignItems: "stretch",
            justifyContent: "center"
        },
        buttonLabel: {
            textAlign: "center",
            color: "#fff",
            fontSize: 16,
            shadowColor: "#999",
            shadowOpacity: 0.3
        },
        bottomBar: {
            height: 40
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
        wrapper: {
            flex: 1,
            backgroundColor: '#fff',
            alignItems: 'stretch',
            justifyContent: 'center',
        },
        container: {
            flex: 1,
            backgroundColor: '#fff',
            borderWidth: 1,
            borderColor: '#000',
            alignItems: 'stretch',
            justifyContent: 'center',
        },
        relationship: {
            flexDirection: "row",
            paddingHorizontal: 20,
            paddingVertical: 5
        },
        relName: {
            flex: 1
        }
    });
