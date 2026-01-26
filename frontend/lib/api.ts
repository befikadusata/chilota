// TODO: Replace with actual API calls to the backend

export const login = async (email, password) => {
  console.log('Logging in with:', email, password);
  // Simulate an API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        id: '1',
        email,
        role: 'worker',
      });
    }, 1000);
  });
};

export const register = async (fullName, email, password, role) => {
  console.log('Registering with:', fullName, email, password, role);
  // Simulate an API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        id: '2',
        email,
        role,
      });
    }, 1000);
  });
};
