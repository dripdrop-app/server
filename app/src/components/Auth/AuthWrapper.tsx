import { useMemo } from 'react';
import { useCheckSessionQuery } from '../../api';

interface AuthWrapperProps {
	render: (user: User) => JSX.Element;
	altRender?: JSX.Element;
}

const AuthWrapper = (props: AuthWrapperProps) => {
	const sessionStatus = useCheckSessionQuery();

	return useMemo(() => {
		if (sessionStatus.isSuccess && sessionStatus.currentData) {
			return props.render(sessionStatus.currentData);
		}
		return props.altRender ?? null;
	}, [props, sessionStatus.currentData, sessionStatus.isSuccess]);
};

export default AuthWrapper;
