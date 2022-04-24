import { useMemo } from 'react';
import { CircularProgress, Stack } from '@mui/material';
import { useCheckSessionQuery } from '../../api';

interface AuthWrapperProps {
	render: (user: User) => JSX.Element;
	altRender?: JSX.Element;
	showLoading?: boolean;
}

const AuthWrapper = (props: AuthWrapperProps) => {
	const sessionStatus = useCheckSessionQuery();

	return useMemo(() => {
		if (sessionStatus.isFetching && props.showLoading) {
			return (
				<Stack padding={10} direction="row" justifyContent="center">
					<CircularProgress />
				</Stack>
			);
		} else if (sessionStatus.isSuccess && sessionStatus.currentData) {
			return props.render(sessionStatus.currentData);
		}
		return props.altRender ?? null;
	}, [props, sessionStatus.currentData, sessionStatus.isFetching, sessionStatus.isSuccess]);
};

export default AuthWrapper;
