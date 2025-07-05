import React, { useState, useEffect } from 'react';
import { AppBar, Toolbar, Typography, CssBaseline, Drawer, List, ListItem, ListItemIcon, ListItemText, Box, Container, Paper, Grid, Card, CardContent, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Divider, Avatar, CircularProgress } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import BarChartIcon from '@mui/icons-material/BarChart';
import TableChartIcon from '@mui/icons-material/TableChart';

const drawerWidth = 220;

const menuItems = [
  { key: 'Dashboard', icon: <DashboardIcon />, label: 'Dashboard' },
  { key: 'Analytics', icon: <BarChartIcon />, label: 'Analytics' },
  { key: 'Reports', icon: <TableChartIcon />, label: 'Reports' },
];

export default function App() {
  const [selected, setSelected] = useState('Dashboard');
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:5000/api/summary')
      .then((res) => {
        if (!res.ok) throw new Error('Network response was not ok');
        return res.json();
      })
      .then((data) => {
        setSummary(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, bgcolor: '#212121' }}>
        <Toolbar>
          <Typography variant="h6" noWrap component="div">
            BizIP Business Intelligence Platform
          </Typography>
        </Toolbar>
      </AppBar>
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: {
            width: drawerWidth,
            boxSizing: 'border-box',
            bgcolor: '#181c24',
            color: '#fff',
            borderRight: 'none',
          },
        }}
      >
        <Toolbar />
        {/* Logo/Avatar */}
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 2 }}>
          <Avatar sx={{ width: 56, height: 56, mb: 1, bgcolor: '#1976d2', fontWeight: 'bold', fontSize: 28 }}>B</Avatar>
          <Typography variant="subtitle1" sx={{ color: '#fff', fontWeight: 600 }}>BizIP</Typography>
        </Box>
        <Divider sx={{ bgcolor: '#232a36', mb: 1 }} />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            {menuItems.map((item) => (
              <ListItem
                button
                key={item.key}
                selected={selected === item.key}
                onClick={() => setSelected(item.key)}
                sx={{
                  my: 0.5,
                  mx: 1,
                  borderRadius: 2,
                  transition: 'background 0.2s',
                  backgroundColor: selected === item.key ? '#1976d2' : 'transparent',
                  color: selected === item.key ? '#fff' : '#b0b8c1',
                  '&:hover': {
                    backgroundColor: selected === item.key ? '#1565c0' : '#232a36',
                    color: '#fff',
                  },
                  boxShadow: selected === item.key ? '0 2px 8px 0 rgba(25, 118, 210, 0.15)' : 'none',
                }}
              >
                <ListItemIcon sx={{ color: selected === item.key ? '#fff' : '#b0b8c1', minWidth: 36 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.label} primaryTypographyProps={{ fontWeight: selected === item.key ? 700 : 500 }} />
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, bgcolor: 'background.default', p: 3 }}>
        <Toolbar />
        <Container maxWidth="lg">
          <Grid container spacing={3}>
            {/* Summary Card */}
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h5" component="div">Summary</Typography>
                  <Typography sx={{ mb: 1.5 }} color="text.secondary">
                    Key Metrics
                  </Typography>
                  <Divider sx={{ mb: 1 }} />
                  {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 60 }}>
                      <CircularProgress size={28} />
                    </Box>
                  ) : error ? (
                    <Typography color="error">{error}</Typography>
                  ) : summary ? (
                    <>
                      <Typography variant="body2">Active Users: {summary.active_users}</Typography>
                      <Typography variant="body2">Opportunities: {summary.opportunities}</Typography>
                      <Typography variant="body2">Compliance Alerts: {summary.compliance_alerts}</Typography>
                    </>
                  ) : null}
                </CardContent>
              </Card>
            </Grid>
            {/* Chart Placeholder */}
            <Grid item xs={12} md={8}>
              <Paper sx={{ p: 2, height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography variant="h6" color="text.secondary">[Chart Placeholder]</Typography>
              </Paper>
            </Grid>
            {/* Data Table */}
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>Recent Activity</Typography>
                {loading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 60 }}>
                    <CircularProgress size={28} />
                  </Box>
                ) : error ? (
                  <Typography color="error">{error}</Typography>
                ) : summary ? (
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Name</TableCell>
                          <TableCell align="right">Value</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        <TableRow>
                          <TableCell>Active Users</TableCell>
                          <TableCell align="right">{summary.active_users}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Opportunities</TableCell>
                          <TableCell align="right">{summary.opportunities}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Compliance Alerts</TableCell>
                          <TableCell align="right">{summary.compliance_alerts}</TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </TableContainer>
                ) : null}
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </Box>
  );
}
