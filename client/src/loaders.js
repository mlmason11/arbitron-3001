import axios from 'axios';

export const BookkeeperListLoader = async ({ request }) => {
  const url = new URL(request.url);
  const page = url.searchParams.get('page') || 1;
  const response = await axios.get(`/bookkeepers?page=${page}`);
  return response.data;
};

export const BookkeeperDetailsLoader = async ({ params }) => {
  const { id } = params;
  const response = await axios.get(`/bookkeepers/${id}`);
  return response.data;
};

export const TeamListLoader = async ({ request }) => {
  const url = new URL(request.url);
  const page = url.searchParams.get('page') || 1;
  const response = await axios.get(`/teams?page=${page}`);
  return response.data;
};

export const TeamDetailsLoader = async ({ params }) => {
  const { id } = params;
  const response = await axios.get(`/teams/${id}`);
  return response.data;
};

export const LeagueListLoader = async ({ request }) => {
  const url = new URL(request.url);
  const page = url.searchParams.get('page') || 1;
  const response = await axios.get(`/leagues?page=${page}`);
  return response.data;
};

export const LeagueDetailsLoader = async ({ params }) => {
  const { id } = params;
  const response = await axios.get(`/leagues/${id}`);
  return response.data;
};
