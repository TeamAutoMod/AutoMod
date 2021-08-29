import React from 'react';
import styles from '../../styles/AutomodPlugin.module.css';
import { Formik, Form, Field, FieldArray } from 'formik';
// import { Config } from '../types/Config';
import { Input, Button, Select } from '@chakra-ui/core'



function updateWarns(guild_id: any, warns: string | number, type: string) {

}

function updateThreshold(guild_id: any, warns: string | number, type: string) {

}
export function AutomodPlugin(props: {guild_id: any, is_warns: boolean, type: string, default: any, h1: string, p: string}) {
    return (
        <div className={styles.automod_plugin}>
            <h1>
                {props.h1}
            </h1>
            <p>
                {props.p}
            </p>
            <Formik 
                initialValues={props.is_warns ? {warns: props.default} : {threshold: props.default}}
                onSubmit={({warns, threshold}) => {
                    if (props.is_warns) {
                        updateWarns(props.guild_id, warns, props.type)
                    } else {
                        updateThreshold(props.guild_id, threshold, props.type)
                    }
                }}
            >
            {
                (_props) => (
                    <form onSubmit={_props.handleSubmit}>
                        <Input 
                            type={"text"}
                            maxLength={3} 
                            minLength={1} 
                            name={props.is_warns ? "warns" : "threshold"}
                            onChange={_props.handleChange}
                            defaultValue={props.default}
                        >
                            <Button type={"submit"} children={`Update ${props.is_warns ? "warns" : "threshold"}`} />
                        </Input>
                    </form>
                )
            }
            </Formik>
        </div>
    )
}