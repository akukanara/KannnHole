import { useState, useEffect } from 'react';
import { Card, Text, Badge, Grid, Flex, Box, Button, Dialog, TextField, Switch, Theme, Select } from '@radix-ui/themes';
import { IconPlus, IconSettings, IconTrash, IconPlugConnected, IconWind, IconDeviceFloppy } from '@tabler/icons-react';

interface Proxy {
  name: string;
  type: string;
  localIP: string;
  localPort: number;
  remotePort: number;
  enabled: boolean;
}

interface ClientData {
  client_id: string;
  frpc_config: Proxy[];
}

export default function ClientTunnelManager({ clientId }: { clientId: string }) {
  const [data, setData] = useState<ClientData | null>(null);
  const [loading, setLoading] = useState(true);
  const [newProxy, setNewProxy] = useState<Proxy>({
    name: '',
    type: 'tcp',
    localIP: '127.0.0.1',
    localPort: 80,
    remotePort: 0,
    enabled: true
  });

  useEffect(() => {
    fetch(`/api/clients/${clientId}/tunnels`)
      .then(res => res.json())
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [clientId]);

  const handleSave = (proxies: Proxy[]) => {
    fetch(`/api/clients/${clientId}/tunnels`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ proxies })
    })
    .then(res => res.json())
    .then(() => {
      setData(prev => prev ? { ...prev, frpc_config: proxies } : null);
    });
  };

  const addTunnel = () => {
    if (!data) return;
    const updated = [...data.frpc_config, newProxy];
    handleSave(updated);
    setNewProxy({
      name: '',
      type: 'tcp',
      localIP: '127.0.0.1',
      localPort: 80,
      remotePort: 0,
      enabled: true
    });
  };

  const deleteTunnel = (index: number) => {
    if (!data) return;
    const updated = data.frpc_config.filter((_, i) => i !== index);
    handleSave(updated);
  };

  const toggleTunnel = (index: number) => {
    if (!data) return;
    const updated = [...data.frpc_config];
    updated[index].enabled = !updated[index].enabled;
    handleSave(updated);
  };

  if (loading) {
    return (
      <Theme accentColor="lime" grayColor="sand" radius="large" scaling="100%">
        <Text>Loading tunnels...</Text>
      </Theme>
    );
  }

  if (!data) {
    return (
      <Theme accentColor="lime" grayColor="sand" radius="large" scaling="100%">
        <Text color="red">Failed to load client data.</Text>
      </Theme>
    );
  }

  return (
    <Theme accentColor="lime" grayColor="sand" radius="large" scaling="100%">
      <Box>
        <Flex justify="between" align="center" mb="6">
          <h2 className="text-xl font-semibold text-slate-800">Tunnels for {clientId}</h2>
          <Dialog.Root>
            <Dialog.Trigger>
              <Button color="lime" size="3">
                <IconPlus size={18} className="mr-1" /> Add Tunnel
              </Button>
            </Dialog.Trigger>
            <Dialog.Content maxWidth="450px">
              <Dialog.Title>Add New Tunnel</Dialog.Title>
              <Dialog.Description size="2" mb="4">
                Configure a new port forwarding rule for this client.
              </Dialog.Description>
              
              <Flex direction="column" gap="3">
                <Flex gap="3">
                  <label className="flex-[2]">
                    <Text as="div" size="2" mb="1" weight="bold">Name</Text>
                    <TextField.Root 
                      value={newProxy.name} 
                      onChange={e => setNewProxy({...newProxy, name: e.target.value})}
                      placeholder="e.g. web-app" 
                    />
                  </label>
                  <label className="flex-1">
                    <Text as="div" size="2" mb="1" weight="bold">Protocol</Text>
                    <Select.Root 
                      value={newProxy.type} 
                      onValueChange={val => setNewProxy({...newProxy, type: val})}
                    >
                      <Select.Trigger className="w-full" />
                      <Select.Content>
                        <Select.Item value="tcp">TCP</Select.Item>
                        <Select.Item value="udp">UDP</Select.Item>
                      </Select.Content>
                    </Select.Root>
                  </label>
                </Flex>
                <Flex gap="3">
                  <label className="flex-1">
                    <Text as="div" size="2" mb="1" weight="bold">Local Port</Text>
                    <TextField.Root 
                      type="number"
                      value={newProxy.localPort} 
                      onChange={e => setNewProxy({...newProxy, localPort: parseInt(e.target.value)})}
                    />
                  </label>
                  <label className="flex-1">
                    <Text as="div" size="2" mb="1" weight="bold">Remote Port</Text>
                    <TextField.Root 
                      type="number"
                      value={newProxy.remotePort} 
                      onChange={e => setNewProxy({...newProxy, remotePort: parseInt(e.target.value)})}
                    />
                  </label>
                </Flex>
              </Flex>

              <Flex gap="3" mt="6" justify="end">
                <Dialog.Close>
                  <Button variant="soft" color="gray">Cancel</Button>
                </Dialog.Close>
                <Dialog.Close>
                  <Button color="lime" onClick={addTunnel}>Create Tunnel</Button>
                </Dialog.Close>
              </Flex>
            </Dialog.Content>
          </Dialog.Root>
        </Flex>

        <Grid columns={{ initial: '1', sm: '2' }} gap="4">
          {data.frpc_config.map((proxy, index) => (
            <Card key={index} size="2" className={proxy.enabled ? '' : 'opacity-70 grayscale'}>
              <Flex justify="between" align="center" mb="4">
                <Box>
                  <Text weight="bold" size="3" className="block">{proxy.name}</Text>
                  <Badge color="gray" variant="surface">{proxy.type.toUpperCase()}</Badge>
                </Box>
                <Flex gap="3" align="center">
                  <Switch 
                    checked={proxy.enabled} 
                    onCheckedChange={() => toggleTunnel(index)}
                    color="lime"
                  />
                  <Button variant="ghost" color="red" onClick={() => deleteTunnel(index)}>
                    <IconTrash size={18} />
                  </Button>
                </Flex>
              </Flex>

              <Box className="bg-slate-50 dark:bg-slate-900/50 p-3 rounded-lg">
                <Flex align="center" gap="3" mb="2">
                  <IconPlugConnected size={16} className="text-slate-400" />
                  <Text size="2" className="font-mono">
                    {proxy.localIP}:{proxy.localPort}
                  </Text>
                </Flex>
                <Flex align="center" gap="3">
                  <IconWind size={16} className="text-lime-500" />
                  <Text size="2" className="font-mono font-bold">
                    Remote Port: {proxy.remotePort}
                  </Text>
                </Flex>
              </Box>
            </Card>
          ))}
        </Grid>

        {data.frpc_config.length === 0 && (
          <Card size="3" className="text-center py-12 border-dashed">
            <Text color="gray">No tunnels configured for this client.</Text>
          </Card>
        )}
      </Box>
    </Theme>
  );
}
