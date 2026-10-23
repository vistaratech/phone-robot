import React, { useEffect, useRef, useState } from 'react';
import { Button, SafeAreaView, ScrollView, Text, TextInput, View } from 'react-native';
import { PhoneBotClient, RobotState } from './PhoneBotClient';
import { StandPolicy } from './policy';

export default function App() {
  const client = useRef(new PhoneBotClient()).current;
  const policy = useRef(new StandPolicy()).current;
  const [ip, setIp] = useState('192.168.1.50');
  const [connected, setConnected] = useState(false);
  const [state, setState] = useState<RobotState | null>(null);
  const [running, setRunning] = useState(false);
  const stateRef = useRef<RobotState | null>(null);

  useEffect(() => {
    client.onStatus = setConnected;
    client.onState = (s) => { stateRef.current = s; setState(s); };
    return () => client.disconnect();
  }, [client]);

  // 50 Hz policy loop
  useEffect(() => {
    if (!running) return;
    const t0 = Date.now();
    const id = setInterval(() => {
      client.sendJoints(policy.act(stateRef.current, (Date.now() - t0) / 1000));
    }, 20);
    return () => clearInterval(id);
  }, [running, client, policy]);

  return (
    <SafeAreaView style={{ flex: 1, padding: 16 }}>
      <Text style={{ fontSize: 22, fontWeight: '600' }}>PhoneBot Controller</Text>
      <TextInput value={ip} onChangeText={setIp} autoCapitalize="none"
        style={{ borderWidth: 1, padding: 8, marginVertical: 8 }} />
      <View style={{ flexDirection: 'row', gap: 8 }}>
        <Button title={connected ? 'Disconnect' : 'Connect'}
          onPress={() => (connected ? client.disconnect() : client.connect(`ws://${ip}:8765`))} />
        <Button title="Torque ON" onPress={() => client.setTorque(true)} />
        <Button title="Torque OFF" color="red" onPress={() => { setRunning(false); client.setTorque(false); }} />
      </View>
      <Button title={running ? 'Stop policy' : 'Run stand policy'} onPress={() => setRunning(!running)} />
      <Text style={{ marginTop: 8 }}>
        {connected ? 'connected' : 'offline'} | torque: {String(state?.torque ?? false)}
      </Text>
      <ScrollView>
        {state?.q.map((v, i) => (
          <Text key={i}>J{i + 1}: {v.toFixed(3)} rad   load {state.load[i].toFixed(1)}%</Text>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
