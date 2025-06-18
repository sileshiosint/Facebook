import React, { useEffect, useState } from 'react';
import analyticsService from '../services/analyticsService';
import { Container, Typography, Grid, Paper, Box, CircularProgress, Alert, Select, MenuItem, FormControl, InputLabel } from '@mui/material';

// Import Chart Components
import RiskDistributionChart from '../components/charts/RiskDistributionChart';
import LanguageDistributionChart from '../components/charts/LanguageDistributionChart';
import TopEntitiesChart from '../components/charts/TopEntitiesChart';
import PostsTimeSeriesChart from '../components/charts/PostsTimeSeriesChart';

function AnalyticsPage() {
  const [riskData, setRiskData] = useState(null);
  const [languageData, setLanguageData] = useState(null);
  const [topPersonEntities, setTopPersonEntities] = useState(null);
  const [topOrgEntities, setTopOrgEntities] = useState(null);
  const [timeSeriesData, setTimeSeriesData] = useState(null);
  const [timeSeriesInterval, setTimeSeriesInterval] = useState('day');

  const [loading, setLoading] = useState({
    risk: true,
    language: true,
    topPerson: true,
    topOrg: true,
    timeSeries: true,
  });
  const [error, setError] = useState('');

  const setLoadingState = (key, value) => {
    setLoading(prev => ({ ...prev, [key]: value }));
  };

  useEffect(() => {
    const fetchAllAnalyticsData = async () => {
      setError(''); // Clear previous errors

      // Risk Categories
      try {
        setLoadingState('risk', true);
        const riskCategories = await analyticsService.getRiskCategories();
        setRiskData(riskCategories);
      } catch (err) {
        console.error("Failed to fetch risk categories:", err);
        setError(prev => prev + `Failed to load risk categories. `);
      } finally {
        setLoadingState('risk', false);
      }

      // Language Distribution
      try {
        setLoadingState('language', true);
        const langDistribution = await analyticsService.getLanguageDistribution();
        setLanguageData(langDistribution);
      } catch (err) {
        console.error("Failed to fetch language distribution:", err);
        setError(prev => prev + `Failed to load language distribution. `);
      } finally {
        setLoadingState('language', false);
      }

      // Top PERSON Entities
      try {
        setLoadingState('topPerson', true);
        const topPersons = await analyticsService.getTopEntities({ entity_label: 'PERSON', n: 7 });
        setTopPersonEntities(topPersons);
      } catch (err) {
        console.error("Failed to fetch top PERSON entities:", err);
        setError(prev => prev + `Failed to load top PERSON entities. `);
      } finally {
        setLoadingState('topPerson', false);
      }

      // Top ORG Entities
      try {
        setLoadingState('topOrg', true);
        const topOrgs = await analyticsService.getTopEntities({ entity_label: 'ORG', n: 7 });
        setTopOrgEntities(topOrgs);
      } catch (err) {
        console.error("Failed to fetch top ORG entities:", err);
        setError(prev => prev + `Failed to load top ORG entities. `);
      } finally {
        setLoadingState('topOrg', false);
      }
    };

    fetchAllAnalyticsData();
  }, []); // Fetch all on mount

  useEffect(() => {
    // Fetch Time Series Data separately as interval can change
    const fetchTimeSeries = async () => {
      setLoadingState('timeSeries', true);
      try {
        const tsData = await analyticsService.getPostsTimeSeries({ interval: timeSeriesInterval });
        setTimeSeriesData(tsData);
      } catch (err) {
        console.error(`Failed to fetch time series data for interval ${timeSeriesInterval}:`, err);
        setError(prev => prev + `Failed to load time series data. `);
      } finally {
        setLoadingState('timeSeries', false);
      }
    };
    fetchTimeSeries();
  }, [timeSeriesInterval]);


  return (
    <Container maxWidth="xl"> {/* Using xl for more space for charts */}
      <Typography variant="h4" gutterBottom sx={{ mt: 2, mb: 3 }}>
        OSINT Analytics Dashboard
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Grid container spacing={3}>
        {/* Risk Distribution Chart */}
        <Grid item xs={12} md={6} lg={4}>
          {loading.risk ? <CircularProgress /> : <RiskDistributionChart data={riskData} />}
        </Grid>

        {/* Language Distribution Chart */}
        <Grid item xs={12} md={6} lg={4}>
          {loading.language ? <CircularProgress /> : <LanguageDistributionChart data={languageData} />}
        </Grid>

        {/* Posts Time Series Chart */}
        <Grid item xs={12} lg={8}> {/* Takes more width */}
          <Paper elevation={3} sx={{ p: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="h6" gutterBottom>Posts Over Time</Typography>
              <FormControl size="small" sx={{minWidth: 120}}>
                <InputLabel>Interval</InputLabel>
                <Select
                  value={timeSeriesInterval}
                  label="Interval"
                  onChange={(e) => setTimeSeriesInterval(e.target.value)}
                >
                  <MenuItem value="day">Daily</MenuItem>
                  <MenuItem value="week">Weekly</MenuItem>
                  <MenuItem value="month">Monthly</MenuItem>
                </Select>
              </FormControl>
            </Box>
            {loading.timeSeries ? <CircularProgress /> : <PostsTimeSeriesChart data={timeSeriesData} interval={timeSeriesInterval} />}
          </Paper>
        </Grid>

        {/* Top PERSON Entities Chart */}
        <Grid item xs={12} md={6} lg={4}>
          {loading.topPerson ? <CircularProgress /> : <TopEntitiesChart data={topPersonEntities} entityType="Top People" />}
        </Grid>

        {/* Top ORG Entities Chart */}
        <Grid item xs={12} md={6} lg={4}>
          {loading.topOrg ? <CircularProgress /> : <TopEntitiesChart data={topOrgEntities} entityType="Top Organizations" />}
        </Grid>

        {/* Add more charts or data displays here */}

      </Grid>
    </Container>
  );
}

export default AnalyticsPage;
