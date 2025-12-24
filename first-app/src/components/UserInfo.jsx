import { useAuth } from '../context/AuthContext';

const UserInfo = () => {
  const { user, userType } = useAuth();

  if (!user) return null;

  return (
    <div style={{ padding: '10px', background: '#f0f0f0', borderRadius: '5px' }}>
      <p><strong>User:</strong> {user.first_name} {user.last_name}</p>
      <p><strong>Type:</strong> {userType}</p>
      <p><strong>Email:</strong> {user.email}</p>
    </div>
  );
};

export default UserInfo;
