import { Button } from '@mui/material';
import { useMemo } from 'react';
import { Link } from 'react-router-dom';

interface CustomLinkProps {
	text: string | JSX.Element;
	to?: string;
	href?: string;
	textColor?: string;
	button?: boolean;
}

const CustomLink = (props: CustomLinkProps) => {
	const linkStyle = useMemo(
		() => ({
			color: props.textColor || 'white',
			textDecoration: 'none',
		}),
		[props.textColor]
	);

	const linkProps = useMemo(
		() => ({
			to: props.to,
			href: props.href,
			target: props.href ? '_blank' : '',
		}),
		[props.href, props.to]
	);

	if (props.button) {
		return (
			<Button color="inherit">
				<Link style={linkStyle} {...linkProps}>
					{props.text}
				</Link>
			</Button>
		);
	}

	return (
		<Link style={linkStyle} {...linkProps}>
			{props.text}
		</Link>
	);
};

export default CustomLink;
