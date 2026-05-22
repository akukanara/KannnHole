import { useState, useEffect } from 'react';
import { Card, Text, Badge, Grid, Flex, Box, Button, Theme } from '@radix-ui/themes';
import { IconWind, IconPlugConnected, IconSettings, IconCircleFilled } from '@tabler/icons-react';

interface Tunnel {
  client_id: string;
  name: string;
  type: string;
  local_ip: string;
  local_port: number;
  remote_port: number;
  enabled: boolean;
}

export default function TunnelCards() {
  const [tunnels, setTunnels] = useState<Tunnel[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/tunnels')
      .then((res) => res.json())
      .then((data) => {
        setTunnels(data.tunnels || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <Theme accentColor="lime" grayColor="sand" radius="large" scaling="100%">
        <Text>Loading tunnels...</Text>
      </Theme>
    );
  }

  if (tunnels.length === 0) {
    return (
      <Theme accentColor="lime" grayColor="sand" radius="large" scaling="100%">
        <Card size="3" className="text-center py-12 border-dashed">
          <Text color="gray">No active tunnels found across your clients.</Text>
        </Card>
      </Theme>
    );
  }

  return (
    <Theme accentColor="lime" grayColor="sand" radius="large" scaling="100%">
      <Grid columns={{ initial: '1', sm: '2', lg: '3' }} gap="4">
        {tunnels.map((tunnel, i) => (
          <Card key={`${tunnel.client_id}-${tunnel.name}-${i}`} size="2" className="hover:shadow-md transition-shadow">
            <Flex justify="between" align="start" mb="3">
              <Box>
                <Text weight="bold" size="3" className="block">{tunnel.name}</Text>
                <Text size="1" color="gray">Client: {tunnel.client_id}</Text>
              </Box>
              <Badge color={tunnel.enabled ? 'lime' : 'gray'} variant="soft">
                <IconCircleFilled size={8} className="mr-1" />
                {tunnel.enabled ? 'Active' : 'Disabled'}
              </Badge>
            </Flex>

            <Box className="bg-slate-50 dark:bg-slate-900/50 p-3 rounded-lg mb-4">
              <Flex align="center" gap="3" mb="2">
                <IconPlugConnected size={16} className="text-slate-400" />
                <Text size="2" className="font-mono">
                  {tunnel.local_ip}:{tunnel.local_port}
                </Text>
              </Flex>
              <Flex align="center" gap="3">
                <IconWind size={16} className="text-lime-500" />
                <Text size="2" className="font-mono font-bold">
                  Remote Port: {tunnel.remote_port}
                </Text>
              </Flex>
            </Box>

            <Flex gap="2">
              <a href={`/clients/${tunnel.client_id}/tunnels`} className="w-full">
                <Button variant="soft" color="gray" size="2" className="w-full">
                  <IconSettings size={16} className="mr-1" /> Configure
                </Button>
              </a>
            </Flex>
          </Card>
        ))}
      </Grid>
    </Theme>
  );
}
