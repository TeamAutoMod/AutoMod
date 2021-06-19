import React from 'react';
import { Formik, Form, Field, FieldArray } from 'formik';
import { Button, Input, Select } from '@chakra-ui/core';
import './config.css';



export function ConfigModal({config, roles, channels}) {
    return (
        <div className="config-modal">
            <ul>
                <li>
                    <div className="change-prefix">
                        <h1>Server prefix</h1>
                        <Formik initialValues={{prefix: config.prefix}} onSubmit={({prefix}) => {
                            alert(prefix)
                        }}>
                            {
                                (props) => (
                                    <form onSubmit={props.handleSubmit}>
                                        <Input 
                                            type="text" 
                                            maxLength="25" 
                                            minLength="1" 
                                            name="prefix" 
                                            onChange={props.handleChange} 
                                            defaultValue={config.prefix}
                                        />
                                        <Button 
                                            type="submit" 
                                            children="Update prefix" 
                                            className="btn"
                                        />
                                    </form>
                                )
                            }
                        </Formik>
                    </div>
                </li>
                <li>
                    <div className="change-muterole">
                        <h1>Mute role</h1>
                        <Formik>
                            {
                                (props) => (
                                    <form onSubmit={props.handleSubmit}>
                                        <Select name="muteRole" onChange={props.handleChange}>
                                            <option value={" "} selected={" "}>None</option>
                                            {roles.map((role) => (
                                                <option 
                                                    value={role.id} 
                                                    selected={role.id === config.mute_role ? config.mute_role : ""}
                                                >{role.name}</option>
                                            ))}
                                        </Select>
                                        <Button 
                                            type="submit" 
                                            children="Update role" 
                                            className="btn"
                                        />
                                    </form>
                                )
                            }
                        </Formik>
                    </div>
                </li>
                <li>
                    <div className="change-modlog">
                        <h1>Moderation log</h1>
                        <Formik>
                            {
                                (props) => (
                                    <form onSubmit={props.handleSubmit}>
                                        <Select name="mod_log" onChange={props.handleChange}>
                                            <option value={" "} selected={" "}>None</option>
                                            {channels.map((channel) => (
                                                <option 
                                                    value={channel.id} 
                                                    selected={channel.id === config.mod_log ? config.mod_log : ""}
                                                >{channel.name}</option>
                                            ))}
                                        </Select>
                                        <Button 
                                            type="submit" 
                                            children="Update channel" 
                                            className="btn"
                                        />
                                    </form>
                                )
                            }
                        </Formik>
                    </div>
                </li>
            </ul>
        </div>
    )
}